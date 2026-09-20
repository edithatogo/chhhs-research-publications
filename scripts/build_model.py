"""Build a cache-free research semantic model from auditable inputs."""
from __future__ import annotations
import csv
import json
import uuid
from pathlib import Path
from project_utils import ROOT, m_text, save_json

SOURCE = 'https://www.cairns-hinterland.health.qld.gov.au/hospitals-and-health-centres'
FACILITIES = [
 ('hhs','Cairns and Hinterland HHS','Service-wide', ['Cairns and Hinterland Hospital and Health Service','Cairns & Hinterland Hospital and Health Service','Cairns and Hinterland Hospital & Health Service','Cairns & Hinterland Hospital & Health Service','Cairns and Hinterland Health Service','CHHHS','Cairns Health Service District','Liz Plummer Cancer Care Centre','Tropical Public Health Services','Cairns Sexual Health Service']),
 ('cairns','Cairns Hospital','Cairns',['Cairns Hospital','Cairns Base Hospital']),
 ('atherton','Atherton Hospital','Hinterland',['Atherton Hospital']),
 ('babinda','Babinda Multi-Purpose Health Centre','Hinterland',['Babinda Hospital','Babinda Multi-Purpose Health Centre']),
 ('gordonvale','Gordonvale Hospital','Hinterland',['Gordonvale Hospital']),
 ('herberton','Herberton Hospital','Hinterland',['Herberton Hospital']),
 ('innisfail','Innisfail Hospital','Hinterland',['Innisfail Hospital']),
 ('mareeba','Mareeba Hospital','Hinterland',['Mareeba Hospital']),
 ('mossman','Mossman Multi-Purpose Health Service','Hinterland',['Mossman Hospital','Mossman Multi-Purpose Health Service']),
 ('tully','Tully Hospital','Hinterland',['Tully Hospital']),
 ('yarrabah','Yarrabah Emergency Service','Community',['Yarrabah Emergency Service']),
 ('cairns-north','Cairns North Community Health','Community',['Cairns North Community Health']),
 ('cairns-south','Cairns South Health Facility','Community',['Cairns South Health Facility']),
 ('chillagoe','Chillagoe Primary Health Centre','Community',['Chillagoe Primary Health Centre','Chillagoe Hospital']),
 ('cow-bay','Cow Bay Primary Health Centre','Community',['Cow Bay Primary Health Centre']),
 ('croydon','Croydon Primary Health Centre','Community',['Croydon Primary Health Centre']),
 ('dimbulah','Dimbulah Primary Health Centre','Community',['Dimbulah Primary Health Centre']),
 ('edmonton','Edmonton Community Health Centre','Community',['Edmonton Community Health Centre']),
 ('forsayth','Forsayth Primary Health Centre','Community',['Forsayth Primary Health Centre']),
 ('georgetown','Georgetown Primary Health Centre','Community',['Georgetown Primary Health Centre']),
 ('jumbun','Jumbun Community Health Centre','Community',['Jumbun Community Health Centre']),
 ('malanda','Malanda Primary Health Centre','Community',['Malanda Primary Health Centre']),
 ('millaa-millaa','Millaa Millaa Primary Health Centre','Community',['Millaa Millaa Primary Health Centre']),
 ('mission-beach','Mission Beach Community Health Centre','Community',['Mission Beach Community Health Centre']),
 ('mount-garnet','Mount Garnet Primary Health Centre','Community',['Mount Garnet Primary Health Centre','Mt Garnet Primary Health Centre']),
 ('ravenshoe','Ravenshoe Primary Health Centre','Community',['Ravenshoe Primary Health Centre']),
 ('sub-acute','Cairns Sub-Acute Care Unit','Cairns',['Cairns Sub-Acute Care Unit']),
 ('smithfield','Smithfield Community Health Centre','Community',['Smithfield Community Health Centre']),
]

def uid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'chhhs-research/' + name))

def definitions() -> list[dict]:
    rows=[]
    for key,name,group,aliases in FACILITIES:
        q='('+' OR '.join(f'"{a}"[Affiliation]' for a in aliases)+')'
        if key not in ('hhs','cairns','cairns-north','cairns-south','sub-acute'):
            q+=' AND (Queensland[Affiliation] OR Australia[Affiliation] OR QLD[Affiliation])'
        rows.append(dict(FacilityKey=key,FacilityName=name,FacilityGroup=group,PubMedQuery=q,Active=True,SourceURL=SOURCE))
    return rows

def expression(name: str, value: str) -> dict:
    return {'name':name,'kind':'m','expression':value.splitlines(),'lineageTag':uid('expression/'+name)}

def column(table: str, name: str, data_type: str='string', **extra) -> dict:
    result={'name':name,'dataType':data_type,'sourceColumn':name,'summarizeBy':'none','lineageTag':uid(table+'/'+name)}
    if data_type=='dateTime': result['formatString']='dd MMM yyyy'
    result.update(extra); return result

def table(name: str, cols: list[dict], source: str, hidden: bool=False) -> dict:
    return {'name':name,'isHidden':hidden,'lineageTag':uid(name),'columns':cols,'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':source.splitlines()}}]}

def measure(name: str, dax: str, fmt: str='#,0') -> dict:
    return {'name':name,'expression':dax,'formatString':fmt,'lineageTag':uid('measure/'+name)}

def build() -> None:
    rows=definitions()
    save_json(ROOT/'config/facilities.json',{'version':'2026-09-11-v2','source':SOURCE,'rows':rows})
    with (ROOT/'config/facility-queries.csv').open('w',newline='',encoding='utf-8') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    row_text=',\n'.join('        {'+', '.join([m_text(r[c]) for c in ('FacilityKey','FacilityName','FacilityGroup','PubMedQuery')]+['true'])+'}' for r in rows)
    facility_m='#table(\n    type table [FacilityKey=text, FacilityName=text, FacilityGroup=text, PubMedQuery=text, Active=logical],\n    {\n'+row_text+'\n    }\n)'
    (ROOT/'powerquery/FacilityDefinitions.m').write_text(facility_m+'\n')
    exprs=[expression('pNCBIEmail','"" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=false]'),expression('FacilityDefinitions',facility_m)]
    for name in ('fnParsePubDate','fnNCBIJson','fnPubMedXML','PubMedHarvest','PubMedFullMetadata','PubMedPublications','PubMedAuthorEvidence','PubMedMetadataChunks','PubMedIngestionAudit','DoraSourceObservations','DoraHistoricalMetadata','DoraMetadataChunks','DoraIngestionAudit','DoraHarvest','CanonicalPublications'):
        exprs.append(expression(name,(ROOT/f'powerquery/{name}.m').read_text()))
    types={name:'string' for name in ['CanonicalKey','PMID','Title','Journal','Authors','DOI','PubMedURL','DORAURL','CHHHSAffiliatedAuthors','Abstract','SourceSet','DedupMethod','PublicationDateRaw','PublicationDatePrecision','PublicationMonth','OnlineDateRaw','MatchedFacilities','AttributionStatus','AttributionEvidence','PublicationNotice',
        'PMCID','AuthorORCIDs','FundingType','IsInternalFunding','FunderNames','GrantIDs','ClinicalTrialID','IndigenousHealthFocus','FieldOfResearch','StudyDesign','EuropePMC_OpenAccess','EuropePMC_FullTextURL','OpenAccessStatus','OAUrl','PDFDownloadStatus','LocalPDFPath','PDFDownloadedUTC']}
    types.update({n:'dateTime' for n in ['PublicationDate','OnlineDate','RefreshedAtUTC']})
    types.update({n:'int64' for n in ['PublicationYear','AuthorCount','FacilityMatchCount','EuropePMC_CitedByCount','CitationCount_Crossref','CitationCount_OpenAlex','PDFFileSize']})
    web_url_cols = {'PubMedURL', 'EuropePMC_FullTextURL', 'OAUrl'}
    pub_cols=[column('Publication',name,dt,**({'dataCategory':'WebUrl'} if name in web_url_cols else {})) for name,dt in types.items()]
    publication=table('Publication',pub_cols,'CanonicalPublications[Publications]')
    publication['description']='One row per canonical publication across PubMed and DORA. Source provenance and reconciliation method are retained; attribution remains reviewable.'
    base='VAR MatchedKeys = VALUES(PublicationFacility[CanonicalKey])\nVAR FacilityFiltered = ISFILTERED(Facility) || ISFILTERED(PublicationFacility)\nRETURN COALESCE(IF(FacilityFiltered, CALCULATE(DISTINCTCOUNT(Publication[CanonicalKey]), KEEPFILTERS(TREATAS(MatchedKeys, Publication[CanonicalKey]))), DISTINCTCOUNT(Publication[CanonicalKey])), 0)'
    publication['measures']=[
        measure('Publications',base),
        measure('PubMed Publications','CALCULATE([Publications], KEEPFILTERS(CONTAINSSTRING(Publication[SourceSet], "PubMed")))'),
        measure('DORA Publications','CALCULATE([Publications], KEEPFILTERS(CONTAINSSTRING(Publication[SourceSet], "DORA")))'),
        measure('Cross-source Matches','CALCULATE([Publications], KEEPFILTERS(Publication[SourceSet] = "PubMed; DORA"))'),
        measure('DORA-only Publications','CALCULATE([Publications], KEEPFILTERS(Publication[SourceSet] = "DORA"))'),
        measure('Reconciliation Needs Review','CALCULATE([Publications], KEEPFILTERS(CONTAINSSTRING(Publication[AttributionStatus], "needs review")))'),
        measure('Open Access Publications','CALCULATE([Publications], KEEPFILTERS(Publication[EuropePMC_OpenAccess] = "Y" || Publication[OpenAccessStatus] IN {"Gold", "Green"} || NOT(ISBLANK(Publication[PMCID]))))'),
        measure('Open Access Rate','DIVIDE([Open Access Publications], [Publications])','0.0%'),
        measure('Funded Publications','CALCULATE([Publications], KEEPFILTERS(Publication[FundingType] <> "Unfunded / Departmental" && Publication[FundingType] <> "" && NOT(ISBLANK(Publication[FundingType]))))'),
        measure('Internal CHHHS Funded Publications','CALCULATE([Publications], KEEPFILTERS(Publication[IsInternalFunding] = "Yes"))'),
        measure('First Nations Health Publications','CALCULATE([Publications], KEEPFILTERS(Publication[IndigenousHealthFocus] = "Yes"))'),
        measure('Clinical Trials Count','CALCULATE([Publications], KEEPFILTERS(Publication[ClinicalTrialID] <> "" && NOT(ISBLANK(Publication[ClinicalTrialID]))))'),
        measure('Archived Full-Text Papers','CALCULATE([Publications], KEEPFILTERS(Publication[PDFDownloadStatus] IN {"Downloaded", "Already Exists"}))'),
        measure('Publications Last Complete Month',"VAR StartDate = MAX(ReportingWindow[ReportMonthStart])\nVAR EndDate = MAX(ReportingWindow[ReportMonthEndExclusive])\nRETURN CALCULATE([Publications], REMOVEFILTERS('Date'), DATESBETWEEN('Date'[Date],StartDate,EndDate-1), KEEPFILTERS(Publication[PublicationDatePrecision] IN {\"day\", \"month\"}))"),
        measure('Publications Previous Year Month',"VAR StartDate = EDATE(MAX(ReportingWindow[ReportMonthStart]),-12)\nVAR EndDate = EDATE(MAX(ReportingWindow[ReportMonthEndExclusive]),-12)\nRETURN CALCULATE([Publications], REMOVEFILTERS('Date'), DATESBETWEEN('Date'[Date],StartDate,EndDate-1), KEEPFILTERS(Publication[PublicationDatePrecision] IN {\"day\", \"month\"}))"),
        measure('Monthly Year-on-Year Change','DIVIDE([Publications Last Complete Month]-[Publications Previous Year Month], [Publications Previous Year Month])','0.0%;-0.0%'),
        measure('Publications Last 24 Complete Months',"VAR StartDate = EDATE(MAX(ReportingWindow[ReportMonthEndExclusive]),-24)\nVAR EndDate = MAX(ReportingWindow[ReportMonthEndExclusive])\nRETURN CALCULATE([Publications], KEEPFILTERS(DATESBETWEEN('Date'[Date],StartDate,EndDate-1)))"),
        measure('Publications Without Usable Month',"CALCULATE([Publications], REMOVEFILTERS('Date'), KEEPFILTERS(NOT(Publication[PublicationDatePrecision] IN {\"day\", \"month\"})))"),
        measure('Reporting Month','IF(ISFILTERED(\'Date\'[YearMonth]), IF(HASONEVALUE(\'Date\'[YearMonth]), SELECTEDVALUE(\'Date\'[YearMonth]), "Select one month"), FORMAT(MAX(ReportingWindow[ReportMonthStart]), "MMMM yyyy"))',''),
        measure('Refresh Timestamp UTC','MAX(ReportingWindow[RefreshedAtUTC])','dd MMM yyyy HH:mm "UTC"'),
        measure('Query Warnings','COUNTROWS(FILTER(SearchAudit, SearchAudit[Warnings] <> ""))'),
        measure('Configured Facility Searches','COUNTROWS(Facility)'),
        measure('Register Row Count','VAR N = [Publications] RETURN IF(N > 0, N, BLANK())'),
        measure('Selected Month Publications',"VAR HasSelection = ISFILTERED('Date'[YearMonth])\nVAR ValidSelection = NOT(HasSelection) || HASONEVALUE('Date'[YearMonth])\nVAR StartDate = IF(HasSelection, DATE(YEAR(MIN('Date'[Date])), MONTH(MIN('Date'[Date])), 1), MAX(ReportingWindow[ReportMonthStart]))\nVAR EndDate = EDATE(StartDate, 1)\nRETURN IF(ValidSelection, CALCULATE([Publications], REMOVEFILTERS('Date'), DATESBETWEEN('Date'[Date], StartDate, EndDate-1), KEEPFILTERS(Publication[PublicationDatePrecision] IN {\"day\", \"month\"})), BLANK())"),
        measure('Monthly Register Row Count','VAR N = [Selected Month Publications] RETURN IF(N > 0, N, BLANK())'),
    ]
    facility=table('Facility',[column('Facility',n) for n in ['FacilityKey','FacilityName','FacilityGroup','PubMedQuery']], 'Table.SelectColumns(FacilityDefinitions,{"FacilityKey","FacilityName","FacilityGroup","PubMedQuery"})')
    bridge=table('PublicationFacility',[column('PublicationFacility','CanonicalKey'),column('PublicationFacility','FacilityKey')],'CanonicalPublications[Matches]',True)
    audit=table('SearchAudit',[column('SearchAudit',n,dt) for n,dt in [('FacilityKey','string'),('SearchCount','int64'),('QueryTranslation','string'),('Warnings','string'),('QueryVersion','string'),('RefreshedAtUTC','dateTime')]],'PubMedHarvest[SearchAudit]')
    date_m='''let
    Start = #date(1900,1,1),
    Finish = #date(Date.Year(Date.From(DateTimeZone.SwitchZone(DateTimeZone.FixedUtcNow(),10)))+2,12,31),
    Days = List.Dates(Start,Duration.Days(Finish-Start)+1,#duration(1,0,0,0)),
    A = Table.FromList(Days,Splitter.SplitByNothing(),{"Date"}),
    B = Table.TransformColumnTypes(A,{{"Date",type date}}),
    C = Table.AddColumn(B,"Year",each Date.Year([Date]),Int64.Type),
    D = Table.AddColumn(C,"MonthNumber",each Date.Month([Date]),Int64.Type),
    E = Table.AddColumn(D,"MonthName",each Date.ToText([Date],"MMM","en-AU"),type text),
    F = Table.AddColumn(E,"YearMonth",each Date.ToText([Date],"yyyy-MM","en-AU"),type text),
    G = Table.AddColumn(F,"YearMonthSort",each [Year]*100+[MonthNumber],Int64.Type)
in G'''
    dates=table('Date',[column('Date',n,dt,**extra) for n,dt,extra in [('Date','dateTime',{'isKey':True}),('Year','int64',{}),('MonthNumber','int64',{'isHidden':True}),('MonthName','string',{'sortByColumn':'MonthNumber'}),('YearMonth','string',{'sortByColumn':'YearMonthSort'}),('YearMonthSort','int64',{'isHidden':True})]],date_m)
    dates['dataCategory']='Time'
    window_m='''let
    NowUTC = DateTimeZone.FixedUtcNow(),
    BrisbaneToday = Date.From(DateTimeZone.SwitchZone(NowUTC,10)),
    EndExclusive = Date.StartOfMonth(BrisbaneToday),
    StartDate = Date.AddMonths(EndExclusive,-1)
in #table(type table [ReportMonthStart=date,ReportMonthEndExclusive=date,RefreshedAtUTC=datetime],{{StartDate,EndExclusive,DateTimeZone.RemoveZone(NowUTC)}})'''
    window=table('ReportingWindow',[column('ReportingWindow',n,'dateTime') for n in ['ReportMonthStart','ReportMonthEndExclusive','RefreshedAtUTC']],window_m)
    relationships=[]
    for ft,fc,tt,tc in [('Publication','PublicationDate','Date','Date'),('PublicationFacility','CanonicalKey','Publication','CanonicalKey'),('PublicationFacility','FacilityKey','Facility','FacilityKey'),('SearchAudit','FacilityKey','Facility','FacilityKey')]:
        relationships.append({'name':uid(f'{ft}.{fc}->{tt}.{tc}'),'fromTable':ft,'fromColumn':fc,'toTable':tt,'toColumn':tc,'fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection','isActive':True})
    model={'name':'CHHHS Research Publications','compatibilityLevel':1600,'model':{'culture':'en-AU','defaultPowerBIDataSourceVersion':'powerBI_V3','sourceQueryCulture':'en-AU','tables':[publication,facility,bridge,dates,audit,window],'relationships':relationships,'expressions':exprs,'annotations':[{'name':'PBI_QueryOrder','value':json.dumps(['pNCBIEmail','FacilityDefinitions','fnParsePubDate','fnNCBIJson','fnPubMedXML','PubMedHarvest','PubMedFullMetadata','PubMedPublications','PubMedAuthorEvidence','PubMedMetadataChunks','PubMedIngestionAudit','DoraSourceObservations','DoraHistoricalMetadata','DoraMetadataChunks','DoraIngestionAudit','DoraHarvest','CanonicalPublications','Publication','Facility','PublicationFacility','Date','SearchAudit','ReportingWindow'])},{'name':'PBI_TimeIntelligenceEnabled','value':'0'}]}}
    target=ROOT/'powerbi/CHHHS Research Publications.SemanticModel'
    save_json(ROOT/'audit/model.snapshot.json',model)
    save_json(target/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'5.0','settings':{'qnaEnabled':False}})
    save_json(ROOT/'audit/model-build.json',{'table_count':len(model['model']['tables']),'measure_count':len(publication['measures']),'facility_queries':len(rows),'cached_data_included':False,'native_engine_tested':False})
    (ROOT/'docs/MEASURES.md').write_text('# Measures\n\n'+ '\n\n'.join('## '+m['name']+'\n\n```dax\n'+m['expression']+'\n```' for m in publication['measures'])+'\n')
    print(f'Built {len(rows)} facility searches, {len(model["model"]["tables"])} tables and {len(publication["measures"])} measures.')

if __name__=='__main__': build()
