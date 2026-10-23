"""Create documented PBIR report files; never reuse legacy visual state."""
from __future__ import annotations
import argparse
from contextvars import ContextVar
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from project_utils import ROOT, save_json

REPORT = ROOT/'powerbi/CHHHS Research Publications.Report'
PAGE_LABELS = [
    ('PublicationRegister','CHHHS Publications'),
    ('MonthlyPublications','Monthly Publications'),
    ('SourceReconciliation','Source Reconciliation'),
    ('ClinicalAnalytics','Clinical Analytics'),
    ('FundingOpportunities','Funding Opportunities'),
    ('FundingCalendar','Funding Calendar'),
    ('MyFundingWatchlist','My Funding Watchlist'),
]
BASE = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'
MANIFEST: list[dict] = []
_ACTIVE_TEMP_DIRS: ContextVar[list[tempfile.TemporaryDirectory] | None] = ContextVar('report_temp_dirs', default=None)


def _temporary_directory(*args, **kwargs) -> tempfile.TemporaryDirectory:
    directory = tempfile.TemporaryDirectory(*args, **kwargs)
    active = _ACTIVE_TEMP_DIRS.get()
    if active is not None:
        active.append(directory)
    return directory

def literal(value: str) -> dict:
    return {'expr':{'Literal':{'Value':"'"+value.replace("'","''")+"'"}}}

def field(table: str, name: str, kind: str='Column') -> dict:
    return {kind:{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}

def col(table: str, name: str, label: str|None=None) -> dict:
    return {'field':field(table,name),'queryRef':f'{table}.{name}','nativeQueryRef':name,'displayName':label or name}

def met(name: str, label: str|None=None) -> dict:
    return {'field':field('Publication',name,'Measure'),'queryRef':'Publication.'+name,'nativeQueryRef':name,'displayName':label or name}

def release_col(name: str, label: str|None=None) -> dict:
    return {'field':field('ReleaseMetadata',name),'queryRef':f'ReleaseMetadata.{name}','nativeQueryRef':name,'displayName':label or name}

def grant_col(name: str, label: str|None=None) -> dict:
    return {'field':field('GrantsRegistry',name),'queryRef':f'GrantsRegistry.{name}','nativeQueryRef':name,'displayName':label or name}

def grant_met(name: str, label: str|None=None) -> dict:
    return {'field':field('GrantsRegistry',name,'Measure'),'queryRef':f'GrantsRegistry.{name}','nativeQueryRef':name,'displayName':label or name}

def visual(page: str, name: str, kind: str, title: str, xywh: tuple, roles: dict|None=None, text: str|None=None, sort_field: dict|None=None, descending: bool=False) -> None:
    x,y,w,h=xywh
    order=sum(m['page']==page for m in MANIFEST)
    config={'visualType':kind,'drillFilterOtherVisuals':True}
    if roles:
        config['query']={'queryState':{role:{'projections':projections} for role,projections in roles.items()}}
        if sort_field:
            config['query']['sortDefinition']={'sort':[{'field':sort_field,'direction':'Descending' if descending else 'Ascending'}],'isDefaultSort':False}
    if text is not None:
        font_size = '20px' if name == 'heading' else '14px' if name == 'caption' else '16px'
        config['objects']={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':text,'textStyle':{'fontFamily':'Segoe UI','fontSize':font_size}}]}]}}]}
    config['visualContainerObjects'] = {
        'title': [{'properties': {
            'show': {'expr': {'Literal': {'Value': 'false' if kind == 'textbox' else 'true'}}},
            'text': literal(title),
            'fontSize': {'expr': {'Literal': {'Value': '15D'}}},
        }}]
    }
    if kind in ('lineChart','clusteredColumnChart','barChart'):
        config.setdefault('objects',{})['valueAxis']=[{'properties':{'logAxisScale':{'expr':{'Literal':{'Value':'false'}}}}}]
    if kind=='tableEx':
        config.setdefault('objects',{})['columnHeaders']=[{'properties':{'wordWrap':{'expr':{'Literal':{'Value':'true'}}}}}]
        config['objects']['values']=[{'properties':{'wordWrap':{'expr':{'Literal':{'Value':'true'}}}}}]
    if kind=='card':
        is_footer = 'refresh' in name or 'footer' in name
        font_size = '16D' if is_footer else '30D'
        config.setdefault('objects',{})['labels']=[{'properties':{'fontSize':{'expr':{'Literal':{'Value':font_size}}}}}]
        config['objects']['categoryLabels']=[{'properties':{'show':{'expr':{'Literal':{'Value':'false'}}}}}]
    if kind=='slicer':
        config.setdefault('objects',{})['data']=[{'properties':{'mode':{'expr':{'Literal':{'Value':"'Dropdown'"}}}}}]
        config['objects']['header']=[{'properties':{'show':{'expr':{'Literal':{'Value':'false'}}}}}]
    obj={'$schema':BASE+'visualContainer/2.0.0/schema.json','name':name,'position':{'x':x,'y':y,'z':order,'width':w,'height':h,'tabOrder':order},'visual':config}
    save_json(REPORT/f'definition/pages/{page}/visuals/{name}/visual.json',obj)
    MANIFEST.append({'page':page,'visual':name,'type':kind,'title':title or text,'position':xywh})

def heading(page: str, title: str, caption: str) -> None:
    visual(page,'heading','textbox','',(32,16,1856,48),text='CHHHS RESEARCH PUBLICATIONS  |  '+title)
    visual(page,'caption','textbox','',(32,64,1856,40),text=caption)

def footer(page: str, text: str) -> None:
    visual(page,'footer','textbox','',(32,1008,1856,48),text=text)

def card(page: str, name: str, title: str, measure: str, index: int) -> None:
    xs = [32, 504, 976, 1448]
    visual(page,name,'card',title,(xs[index],112,440,96),{'Values':[met(measure)]})

def _reject_symlink_components(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ValueError(f'Output path contains a symlink: {current}')


def _validate_candidate(path: Path, selected_pages: list[str] | None) -> Path:
    """Validate a fresh full candidate or complete existing selection target."""
    original = path
    _reject_symlink_components(original)
    candidate = original.resolve(strict=False)
    root = ROOT.resolve()
    if candidate == root or candidate in root.parents or root in candidate.parents:
        raise ValueError('Explicit output directory must be outside the repository tree')
    for protected in (ROOT/'powerbi', ROOT/'config', ROOT/'audit', ROOT/'.git', ROOT/'private'):
        resolved = protected.resolve(strict=False)
        if candidate == resolved or candidate in resolved.parents or resolved in candidate.parents:
            raise ValueError(f'Output directory overlaps protected path: {protected}')
    if candidate.exists() and not candidate.is_dir():
        raise ValueError('Output directory must be a directory')
    if selected_pages:
        required = [candidate/'definition/report.json', candidate/'definition.pbir',
                    candidate/'definition/version.json', candidate/'definition/pages/pages.json',
                    candidate/'StaticResources/SharedResources/BaseThemes/Fluent2-CY26SU08.json']
        required.extend(candidate/'definition/pages'/page/'page.json' for page, _ in PAGE_LABELS)
        missing = [item for item in required if not item.is_file()]
        missing.extend(
            candidate/'definition/pages'/page/'visuals' for page, _ in PAGE_LABELS
            if not any((candidate/'definition/pages'/page/'visuals').glob('*/visual.json'))
        )
        if missing:
            raise ValueError('Page selection requires a complete existing report candidate; missing: '
                             + ', '.join(str(item.relative_to(candidate)) for item in missing))
        for item in candidate.rglob('*'):
            if item.is_symlink():
                raise ValueError(f'Candidate contains a symlink: {item}')
    elif candidate.exists():
        raise ValueError('Full output mode requires a new candidate path')
    if not candidate.parent.is_dir():
        raise ValueError('Output directory parent must already exist')
    return candidate


def _build_report(source_pbix: Path | None = None, output_dir: Path | None = None,
                  selected_pages: list[str] | None = None) -> None:
    MANIFEST.clear()
    global REPORT
    canonical_report = REPORT
    pages = PAGE_LABELS
    if selected_pages is not None:
        if output_dir is None:
            raise ValueError('Page selection requires --output-dir')
        if len(selected_pages) != len(set(selected_pages)):
            raise ValueError('Duplicate page selection')
        unknown = sorted(set(selected_pages) - {page for page, _ in pages})
        if unknown:
            raise ValueError('Unknown page selection: ' + ', '.join(unknown))
    candidate = _validate_candidate(output_dir, selected_pages) if output_dir is not None else None
    theme_name = 'Fluent2-CY26SU08'
    source_theme = None
    if source_pbix is not None:
        _reject_symlink_components(source_pbix)
        source_resolved = source_pbix.resolve(strict=True)
        if candidate is not None and (source_resolved == candidate or source_resolved in candidate.parents
                                      or candidate in source_resolved.parents):
            raise ValueError('Source PBIX overlaps the output candidate')
        if not source_resolved.is_file():
            raise ValueError('Source PBIX must be a file')
        with zipfile.ZipFile(source_resolved) as archive:
            source_theme = archive.read('Report/StaticResources/SharedResources/BaseThemes/'
                                        + theme_name + '.json')
    elif not (canonical_report/'StaticResources/SharedResources/BaseThemes'/f'{theme_name}.json').is_file():
        raise FileNotFoundError('Bundled theme missing. Supply the original PBIX to restore the theme.')

    platform_bytes = None
    if candidate is not None and not selected_pages:
        # A full candidate represents the existing report, including its logical
        # identity. Preserve the source metadata rather than inventing an item.
        platform_bytes = (canonical_report/'.platform').read_bytes()

    scratch = None
    staging = None
    if candidate is None:
        report_root = canonical_report
    elif selected_pages:
        scratch = _temporary_directory(prefix='rims-report-build-')
        report_root = Path(scratch.name)/'report'
    else:
        staging = _temporary_directory(prefix='.rims-report-stage-', dir=candidate.parent)
        report_root = Path(staging.name)
    REPORT = report_root
    if platform_bytes is not None:
        (REPORT/'.platform').write_bytes(platform_bytes)
    # Default mode now overlays generated paths and preserves unrelated/native-only
    # files; explicit candidate mode is staged and promoted only after generation.
    for page,label in pages:
        save_json(REPORT/f'definition/pages/{page}/page.json',{'$schema':BASE+'page/2.0.0/schema.json','name':page,'displayName':label,'displayOption':'FitToPage','height':1080,'width':1920})
    save_json(REPORT/'definition/pages/pages.json',{'$schema':BASE+'pagesMetadata/1.0.0/schema.json','pageOrder':[p for p,_ in pages],'activePageName':'PublicationRegister'})
    save_json(REPORT/'definition/version.json',{'$schema':BASE+'versionMetadata/1.0.0/schema.json','version':'4.0.0'})
    theme_file = REPORT/'StaticResources/SharedResources/BaseThemes'/f'{theme_name}.json'
    if source_theme is not None:
        theme_file.parent.mkdir(parents=True, exist_ok=True); theme_file.write_bytes(source_theme)
    elif not theme_file.exists() and (canonical_report/'StaticResources/SharedResources/BaseThemes'/f'{theme_name}.json').is_file():
        theme_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(canonical_report/'StaticResources/SharedResources/BaseThemes'/f'{theme_name}.json', theme_file)
    elif not theme_file.exists():
        raise FileNotFoundError('Bundled theme missing. Supply the original PBIX to restore the theme.')
    save_json(REPORT/'definition/report.json',{
        '$schema':BASE+'report/3.0.0/schema.json',
        'themeCollection':{'baseTheme':{'name':theme_name,'reportVersionAtImport':{'visual':'2.0.0','report':'3.0.0','page':'2.0.0'},'type':'SharedResources'}},
        'resourcePackages':[{'name':'SharedResources','type':'SharedResources','items':[{'name':theme_name,'path':f'BaseThemes/{theme_name}.json','type':'BaseTheme'}]}],
        'settings':{'useEnhancedTooltips':True,'exportDataMode':'AllowSummarized','isPersistentUserStateDisabled':True}
    })
    save_json(REPORT/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../CHHHS Research Publications.SemanticModel'}}})
    if candidate is None:
        save_json(ROOT/'powerbi/CHHHS Research Publications.pbip',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'CHHHS Research Publications.Report'}}],'settings':{'enableAutoRecovery':True}})

    # Page 1: CHHHS Publications (PublicationRegister)
    p='PublicationRegister'
    heading(p,'CHHHS Publications','PubMed and DORA publication records. Counts remain provisional while identity and institutional scope reviews are open.')
    for i,(n,t,m) in enumerate([
        ('all-papers','Canonical publications','Publications'),
        ('pubmed','Found in PubMed','PubMed Publications'),
        ('dora','Found in DORA','DORA Publications'),
        ('overlap','Found in both sources','Cross-source Matches')
    ]): card(p,n,t,m,i)
    visual(p,'facility-filter','slicer','Facility / service',(32,224,520,72),{'Values':[col('Facility','FacilityName','Facility / service')]})
    visual(p,'year-filter','slicer','Publication year',(568,224,280,72),{'Values':[col('Publication','PublicationYear','Year')]})
    visual(p,'source-filter','slicer','Source provenance',(864,224,440,72),{'Values':[col('Publication','SourceSet','Source')]})
    visual(p,'review-filter','slicer','Attribution status',(1320,224,568,72),{'Values':[col('Publication','AttributionStatus','Status')]})
    
    # Executive Analytics Visuals (Replacing raw publication title table)
    visual(p,'annual-trajectory','lineChart','Annual publication trajectory',(32,312,912,312),{
        'Category':[col('Publication','PublicationYear','Year')],
        'Y':[met('Publications','Publications')]
    },sort_field=field('Publication','PublicationYear'),descending=False)
    
    visual(p,'facility-breakdown','barChart','Publications by CHHHS facility / service',(960,312,928,312),{
        'Category':[col('Facility','FacilityName','Facility')],
        'Y':[met('Publications','Publications')]
    },sort_field=field('Publication','Publications','Measure'),descending=True)
    
    visual(p,'attribution-breakdown','barChart','Institutional attribution status breakdown',(32,640,912,304),{
        'Category':[col('Publication','AttributionStatus','Attribution')],
        'Y':[met('Publications','Publications')]
    },sort_field=field('Publication','Publications','Measure'),descending=True)
    
    visual(p,'provenance-breakdown','donutChart','Source provenance distribution',(960,640,928,304),{
        'Category':[col('Publication','SourceSet','Source')],
        'Y':[met('Publications','Publications')]
    })
    
    visual(p,'release-provenance','tableEx','Release provenance',(32,960,1856,80),{'Values':[
        release_col('SoftwareVersion','Software version'),
        release_col('AcceptedBatchID','Accepted batch identity')
    ]})

    # Page 2: Monthly Publications (MonthlyPublications)
    p='MonthlyPublications'
    heading(p,'Monthly Publications','Select one publication month; clear the selection for the previous complete Brisbane month. Publication dates determine inclusion.')
    for i,(n,t,m) in enumerate([
        ('month','Reporting month','Reporting Month'),
        ('monthly-papers','Publications in reporting month','Selected Month Publications'),
        ('undated','Records without usable month','Publications Without Usable Month')
    ]):
        visual(p,n,'card',t,(32+472*(3 if n=='undated' else i),112,440,96),{'Values':[met(m)]})
    visual(p,'month-yoy','slicer','Publication month (choose one; clear for default)',(976,112,440,96),{'Values':[col('Date','YearMonth','Month')]})
    visual(p,'publication-trend','barChart','Facility / service matches in reporting month (overlapping)',(32,224,1200,328),{'Category':[col('Facility','FacilityName','Facility')],'Y':[met('Selected Month Publications','Publications')]},sort_field=field('Publication','Selected Month Publications','Measure'),descending=True)
    visual(p,'monthly-source','donutChart','Source provenance',(1256,224,632,328),{'Category':[col('Publication','SourceSet','Source')],'Y':[met('Selected Month Publications','Publications')]})
    
    # Executive Monthly Analytics (Replacing raw monthly title table)
    visual(p,'monthly-history-trend','lineChart','Monthly publication trend (Last 24 complete months)',(32,568,1200,432),{
        'Category':[col('Date','YearMonth','Month')],
        'Y':[met('Publications Last 24 Complete Months','Publications')]
    })
    visual(p,'monthly-attribution','barChart','Reporting month attribution status',(1256,568,632,432),{
        'Category':[col('Publication','AttributionStatus','Attribution')],
        'Y':[met('Selected Month Publications','Publications')]
    },sort_field=field('Publication','Selected Month Publications','Measure'),descending=True)
    
    footer(p,'Indexing delays can revise prior months. Partial and absent dates are not silently assigned to January or the refresh date.')

    # Page 3: Source Reconciliation (SourceReconciliation)
    p='SourceReconciliation'
    heading(p,'Source Reconciliation','Audit PubMed and DORA coverage, deduplication and institutional-attribution evidence before using counts externally.')
    for i,(n,t,m) in enumerate([
        ('pubmed','PubMed publications','PubMed Publications'),
        ('dora','DORA publications','DORA Publications'),
        ('dora-only','DORA-only publications','DORA-only Publications'),
        ('needs-review','Needs reconciliation review','Reconciliation Needs Review')
    ]): card(p,n,t,m,i)
    visual(p,'source-overlap','donutChart','Canonical publications by source provenance',(32,224,736,312),{'Category':[col('Publication','SourceSet','Source')],'Y':[met('Publications')]})
    visual(p,'dedup-method','barChart','Reconciliation method',(792,224,528,312),{'Category':[col('Publication','DedupMethod','Method')],'Y':[met('Publications')]},sort_field=field('Publication','Publications','Measure'),descending=True)
    visual(p,'facility-contributions','tableEx','PubMed search coverage and warnings',(1344,224,544,312),{'Values':[col('SearchAudit','FacilityKey','Search key'),col('SearchAudit','SearchCount','Source matches'),col('SearchAudit','Warnings','Warnings'),col('SearchAudit','QueryVersion','Query version')]})
    visual(p,'reconciliation-register','tableEx','Reconciliation and attribution register',(32,552,1856,352),{'Values':[
        col('Publication','Title','Publication'),col('Publication','AttributionEvidence','Attribution evidence'),col('Publication','SourceSet','Source'),
        col('Publication','DedupMethod','Deduplication'),col('Publication','AttributionStatus','Attribution status'),
        col('Publication','CHHHSAffiliatedAuthors','DORA CHHHS-affiliated author(s)'),col('Publication','MatchedFacilities','PubMed facility/service matches'),
        col('Publication','PMID','PMID'),col('Publication','DORAURL','DORA')
    ]})
    visual(p,'refresh-time','card','Last model refresh (UTC)',(32,912,584,96),{'Values':[met('Refresh Timestamp UTC')]})
    visual(p,'warnings','card','PubMed queries with warnings',(640,912,584,96),{'Values':[met('Query Warnings')]})
    visual(p,'searches','card','Configured PubMed affiliation searches',(1248,912,640,96),{'Values':[met('Configured Facility Searches')]})
    footer(p,'Identifier conflicts and title/year candidates remain separate for review. Counts reconcile to the retained source snapshot; institutional attribution remains provisional.')

    # Page 4: Clinical Analytics & Research Intelligence (ClinicalAnalytics)
    p='ClinicalAnalytics'
    heading(p,'Clinical Analytics','Clinical directorate specialty mapping, ANZSRC Field of Research (FoR) classification, Open Access compliance, and clinical trial activity.')
    for i,(n,t,m) in enumerate([
        ('oa-rate','Open access compliance rate','Open Access Rate'),
        ('oa-papers','Open access publications','Open Access Publications'),
        ('trials-count','Clinical trial linked papers','Clinical Trials Count'),
        ('funded-papers','Grant-funded publications','Funded Publications')
    ]): card(p,n,t,m,i)
    
    visual(p,'facility-filter','slicer','Clinical facility / service',(32,224,608,72),{'Values':[col('Facility','FacilityName','Facility / service')]})
    visual(p,'year-filter','slicer','Publication year',(656,224,304,72),{'Values':[col('Publication','PublicationYear','Year')]})
    visual(p,'oa-filter','slicer','Open access status',(976,224,440,72),{'Values':[col('Publication','OpenAccessStatus','Open Access')]})
    visual(p,'study-filter','slicer','Study design',(1432,224,456,72),{'Values':[col('Publication','StudyDesign','Study Design')]})

    visual(p,'specialty-distribution','barChart','Publications by clinical directorate and specialty',(32,312,912,312),{
        'Category':[col('Facility','FacilityName','Facility / Directorate')],
        'Y':[met('Publications','Publications')]
    },sort_field=field('Publication','Publications','Measure'),descending=True)
    
    visual(p,'for-division','barChart','ANZSRC 2020 Field of Research (FoR) division',(960,312,928,312),{
        'Category':[col('Publication','FieldOfResearch','FoR Division')],
        'Y':[met('Publications','Publications')]
    },sort_field=field('Publication','Publications','Measure'),descending=True)

    visual(p,'oa-distribution','donutChart','Open access distribution (Gold / Green / Hybrid / Closed)',(32,640,912,304),{
        'Category':[col('Publication','OpenAccessStatus','Open Access')],
        'Y':[met('Publications','Publications')]
    })

    visual(p,'study-design-breakdown','barChart','Evidence hierarchy and study designs',(960,640,928,304),{
        'Category':[col('Publication','StudyDesign','Study Design')],
        'Y':[met('Publications','Publications')]
    },sort_field=field('Publication','Publications','Measure'),descending=True)

    visual(p,'footer','textbox','',(32,952,1856,48),text='Field of Research mapped using ANZSRC 2020 2-digit divisions. Open access classification verified via Europe PMC and OpenAlex APIs in accordance with the NHMRC Open Access Policy.')

    # Page 5: Funding Opportunities (FundingOpportunities)
    p='FundingOpportunities'
    heading(p,'Funding Opportunities','Filter the registry by opportunity status, CHHHS relevance, review state, source, eligibility, deadline and funder. Registry ingestion and review state are pending native acceptance.')
    for i,(n,t,m) in enumerate([
        ('grant-count','Opportunities','Grant Opportunities'),
        ('grant-open','Open opportunities','Open Grant Opportunities'),
        ('grant-review','Needs review','Grant Opportunities Needing Review'),
    ]):
        visual(p,n,'card',t,(32+472*i,112,440,96),{'Values':[grant_met(m)]})
    funding_filters = [
        ('grant-status-filter','Opportunity status',grant_col('Status','Status')),
        ('grant-relevance-filter','CHHHS relevance',grant_col('CHHHSRelevance','Relevance')),
        ('grant-review-filter','Review state',grant_col('ReviewStatus','Review status')),
        ('grant-source-filter','Source',grant_col('Source','Source')),
        ('grant-eligibility-filter','Eligibility',grant_col('Eligibility','Eligibility')),
        ('grant-deadline-filter','External deadline',grant_col('Deadline','Deadline')),
        ('grant-funder-filter','Funder',grant_col('Funder','Funder')),
    ]
    for i,(name,title,projection) in enumerate(funding_filters):
        # Keep the six existing filters in place and add Funder below them.
        x = 32 + 312 * (i % 6)
        y = 224 + 80 * (i // 4)
        visual(p,name,'slicer',title,(x,y,296,72),{'Values':[projection]})
    visual(p,'grant-register','tableEx','Opportunity register',(32,408,1856,480),{'Values':[
        grant_col('Title','Opportunity'),grant_col('Funder'),grant_col('Source'),grant_col('Eligibility'),grant_col('Deadline'),
        grant_col('DeadlinePrecision','Deadline precision'),grant_col('Status'),grant_col('CHHHSRelevance','CHHHS relevance'),
        grant_col('ReviewStatus','Review status'),grant_col('URL','Source link')
    ]})
    footer(p,'Source links and review state are required. A blank or failed source batch must not replace the last accepted registry.')

    # Page 6: Funding Calendar (FundingCalendar)
    p='FundingCalendar'
    heading(p,'Funding Calendar','External deadlines are distinct from future institutional dates. Partial and uncertain dates remain visible for review.')
    visual(p,'calendar-status-filter','slicer','Status',(32,112,440,72),{'Values':[grant_col('Status','Status')]})
    visual(p,'calendar-precision-filter','slicer','Deadline precision',(504,112,440,72),{'Values':[grant_col('DeadlinePrecision','Precision')]})
    visual(p,'calendar-source-filter','slicer','Funder / source',(976,112,440,72),{'Values':[grant_col('Funder','Funder')]})
    visual(p,'calendar-register','tableEx','Funding calendar data',(32,224,1856,632),{'Values':[
        grant_col('DeadlineBrisbaneDate','Brisbane date'),grant_col('DeadlineBrisbaneTime','Brisbane time'),
        grant_col('DeadlineTimezone','Source timezone'),grant_col('DeadlineTemporalStatus','Time resolution'),
        grant_col('Deadline','Source deadline'),grant_col('DeadlinePrecision','Precision'),grant_col('Title','Opportunity'),
        grant_col('Funder'),grant_col('RoundID','Round'),grant_col('Status'),grant_col('CHHHSRelevance','CHHHS relevance'),
        grant_col('URL','Source link')
    ]})
    visual(p,'calendar-note','textbox','',(32,896,1856,72),text='Institutional dates, holiday calendars and reminders are policy-driven additions and are not yet persisted in the native registry.')
    footer(p,'Never infer a day from a month or year-only deadline. Preserve source-stated date precision and timezone uncertainty.')

    # Page 7: My Funding Watchlist (MyFundingWatchlist)
    p='MyFundingWatchlist'
    heading(p,'My Funding Watchlist','A personal view is designed as a private subscription surface; persistence and delivery remain pending native SharePoint/Power Apps acceptance.')
    visual(p,'watchlist-relevance-filter','slicer','CHHHS relevance',(32,112,520,72),{'Values':[grant_col('CHHHSRelevance','Relevance')]})
    visual(p,'watchlist-review-filter','slicer','Review state',(584,112,520,72),{'Values':[grant_col('ReviewStatus','Review status')]})
    visual(p,'watchlist-note','textbox','',(1136,112,752,72),text='Watchlist filters are a report preview; no personal subscription or notification is created by this PBIP.')
    visual(p,'watchlist-register','tableEx','Candidate watchlist',(32,224,1856,632),{'Values':[
        grant_col('Title','Opportunity'),grant_col('Funder'),grant_col('Deadline'),grant_col('Status'),
        grant_col('CHHHSRelevance','Relevance'),grant_col('ReviewStatus','Review status'),grant_col('ReviewNotes','Review notes'),grant_col('URL','Source link')
    ]})
    footer(p,'Personal subscriptions, categories, individual-grant watches and reminder/calendar delivery require an authenticated list-backed preference surface.')

    if candidate is None:
        save_json(ROOT/'audit/report-build.json',{'pages':len(pages),'visuals':len(MANIFEST),'manifest':MANIFEST,'legacy_visuals_copied':0,'legacy_filters_copied':0,'native_render_tested':False})
    if selected_pages:
        staging = _temporary_directory(prefix='.rims-report-stage-', dir=candidate.parent)
        staged_candidate = Path(staging.name)
        shutil.copytree(candidate, staged_candidate, dirs_exist_ok=True, copy_function=shutil.copy2)
        for page in selected_pages:
            shutil.copytree(report_root/'definition/pages'/page,
                            staged_candidate/'definition/pages'/page, dirs_exist_ok=True, copy_function=shutil.copy2)
        scratch.cleanup()
        scratch = None
        backup_dir = tempfile.TemporaryDirectory(prefix='.rims-report-rollback-', dir=candidate.parent)
        backup = Path(backup_dir.name)
        backup_dir.cleanup()
        os.replace(candidate, backup)
        try:
            os.replace(staged_candidate, candidate)
        except OSError as promotion_error:
            try:
                os.replace(backup, candidate)
            except OSError as rollback_error:
                raise RuntimeError(
                    f'Report promotion failed ({promotion_error}); rollback also failed '
                    f'({rollback_error}); prior candidate is preserved at {backup}'
                ) from rollback_error
            raise
        for child in sorted(backup.rglob('*'), key=lambda item: len(item.parts), reverse=True):
            child.rmdir() if child.is_dir() else child.unlink()
        backup.rmdir()
        staging.cleanup()
        staging = None
    elif candidate is not None:
        os.replace(report_root, candidate)
        staging.cleanup()
        staging = None
    REPORT = canonical_report
    if scratch is not None:
        scratch.cleanup()
    if staging is not None:
        staging.cleanup()
    print(f'Built {len(pages)} pages and {len(MANIFEST)} research-only visuals.')


def build(source_pbix: Path | None = None, output_dir: Path | None = None,
          selected_pages: list[str] | None = None) -> None:
    global REPORT
    original_report = REPORT
    active: list[tempfile.TemporaryDirectory] = []
    token = _ACTIVE_TEMP_DIRS.set(active)
    try:
        _build_report(source_pbix, output_dir, selected_pages)
    finally:
        for directory in reversed(active):
            directory.cleanup()
        _ACTIVE_TEMP_DIRS.reset(token)
        REPORT = original_report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source_pbix',type=Path,nargs='?')
    parser.add_argument('--output-dir',type=Path,help='New isolated report item root on an existing parent path')
    parser.add_argument('--page',action='append',dest='pages',help='Existing exact page name; repeat to select pages')
    args=parser.parse_args();build(args.source_pbix,args.output_dir,args.pages)
