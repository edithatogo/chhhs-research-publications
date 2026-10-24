/** Side-effect-free Office Scripts producer for the already-admitted NIH FON.
 * Acquisition, retained bytes, conditional commits and refresh remain in the flow.
 * No workbook writes, network calls, identity assertions or effective-date guesses.
 */
type Value = null | boolean | number | string | Value[] | { [key: string]: Value };
type Obj = { [key: string]: Value };
function requireThat(ok: boolean, code: string): void { if (!ok) throw new Error(code); }
function object(value: Value): Obj { requireThat(value !== null && typeof value === 'object' && !Array.isArray(value), 'NIH_EXPECTED_OBJECT'); return value as Obj; }
function text(value: Value): string { requireThat(typeof value === 'string', 'NIH_EXPECTED_TEXT'); return value as string; }
function list(value: Value): Value[] { requireThat(Array.isArray(value), 'NIH_EXPECTED_ARRAY'); return value as Value[]; }
function canonical(value: Value): string {
  if (Array.isArray(value)) return '[' + value.map(v => canonical(v)).join(',') + ']';
  if (value !== null && typeof value === 'object') return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
  requireThat(typeof value !== 'number' || Number.isFinite(value), 'NIH_NONFINITE_NUMBER');
  return JSON.stringify(value);
}
function bytes(s: string): number[] {
  const out: number[] = [];
  for (const char of s) { const n = char.codePointAt(0) as number;
    requireThat(n < 0xd800 || n > 0xdfff, 'NIH_UNPAIRED_SURROGATE');
    if (n < 128) out.push(n);
    else if (n < 2048) out.push(192 | (n >> 6), 128 | (n & 63));
    else if (n < 65536) out.push(224 | (n >> 12), 128 | ((n >> 6) & 63), 128 | (n & 63));
    else out.push(240 | (n >> 18), 128 | ((n >> 12) & 63), 128 | ((n >> 6) & 63), 128 | (n & 63));
  } return out;
}
function sha256(input: number[]): string {
  const k = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  const h = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const a = input.slice(); const bitLength = a.length * 8; a.push(128);
  while (a.length % 64 !== 56) a.push(0);
  for (let i=7;i>=0;i--) a.push(Math.floor(bitLength / Math.pow(256,i)) & 255);
  const rr = (n: number, b: number): number => (n >>> b) | (n << (32-b));
  for (let offset=0;offset<a.length;offset+=64) {
    const w: number[] = [];
    for(let i=0;i<16;i++) w.push((a[offset+4*i]<<24)|(a[offset+4*i+1]<<16)|(a[offset+4*i+2]<<8)|a[offset+4*i+3]);
    for(let i=16;i<64;i++) { const x=w[i-15],y=w[i-2]; w.push((w[i-16]+(rr(x,7)^rr(x,18)^(x>>>3))+w[i-7]+(rr(y,17)^rr(y,19)^(y>>>10)))|0); }
    let [b,c,d,e,f,g,j,l] = h;
    for(let i=0;i<64;i++) { const t1=(l+(rr(f,6)^rr(f,11)^rr(f,25))+((f&g)^(~f&j))+k[i]+w[i])|0; const t2=((rr(b,2)^rr(b,13)^rr(b,22))+((b&c)^(b&d)^(c&d)))|0; l=j;j=g;g=f;f=(e+t1)|0;e=d;d=c;c=b;b=(t1+t2)|0; }
    const q=[b,c,d,e,f,g,j,l]; for(let i=0;i<8;i++) h[i]=(h[i]+q[i])|0;
  } return h.map(n=>(n>>>0).toString(16).padStart(8,'0')).join('');
}
function binary(s: string): number[] {
  requireThat(s.length > 0 && s.length % 4 === 0 && /^[A-Za-z0-9+/]*={0,2}$/.test(s), 'NIH_INVALID_BASE64');
  const alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'; const out: number[]=[];
  for(let i=0;i<s.length;i+=4) { const n=(alphabet.indexOf(s[i])<<18)|(alphabet.indexOf(s[i+1])<<12)|((s[i+2]==='='?0:alphabet.indexOf(s[i+2]))<<6)|(s[i+3]==='='?0:alphabet.indexOf(s[i+3])); out.push((n>>>16)&255);if(s[i+2]!=='=')out.push((n>>>8)&255);if(s[i+3]!=='=')out.push(n&255); }
  return out;
}
function pyrepr(s: string): string {
  const quote = s.includes("'") && !s.includes('"') ? '"' : "'"; let result=quote;
  for(const ch of s) { const n=ch.codePointAt(0) as number;
    if(ch===quote||ch==='\\') result+='\\'+ch;
    else if(ch==='\n')result+='\\n';else if(ch==='\r')result+='\\r';else if(ch==='\t')result+='\\t';
    else if(ch!==' ' && /[\p{C}\p{Z}]/u.test(ch)) result+='\\'+(n<256?'x'+n.toString(16).padStart(2,'0'):n<65536?'u'+n.toString(16).padStart(4,'0'):'U'+n.toString(16).padStart(8,'0'));
    else result+=ch;
  } return result+quote;
}
function semantic(detail: Obj): string {
  const copy=object(JSON.parse(JSON.stringify(detail)) as Value);
  const history=list(copy.opportunityHistoryDetails);
  for(const item of [copy, ...history.map(x=>object(x))]) {
    const synopsis=object(item.synopsis); const categories=list(synopsis.applicantTypes).map(x=>object(x));
    requireThat(categories.length>0 && categories.every(x=>typeof x.id==='string' && !!x.id && typeof x.description==='string') && new Set(categories.map(x=>text(x.id))).size===categories.length,'NIH_INVALID_APPLICANT_CATEGORIES');
    synopsis.applicantTypes=categories.sort((a,b)=>text(a.id)<text(b.id)?-1:text(a.id)>text(b.id)?1:0);
  } return canonical(copy);
}
function normalizedText(s: Value): string { return s===undefined||s===null?'':text(s).replace(/[\s\u001c-\u001f]+/gu,' ').trim(); }
function main(workbook: ExcelScript.Workbook, payload: string): string {
  requireThat(payload.length<=2000000,'NIH_WORKER_INPUT_TOO_LARGE');
  const input=object(JSON.parse(payload) as Value), context=object(input.context);
  requireThat(context.schema==='rims-nih-admitted-context-v1','NIH_CONTEXT_SCHEMA');
  const observed=text(input.observed_utc);
  requireThat(/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,7})?Z$/.test(observed) && Number.isFinite(Date.parse(observed)),'NIH_INVALID_OBSERVATION');
  const entries=list(input.responses).map(x=>object(x)); const roles=['search-current','detail-current','search-replay','detail-replay'];
  requireThat(entries.length===4 && entries.every((x,i)=>x.role===roles[i] && x.http_status===200),'NIH_INCOMPLETE_RESPONSES');
  const envelopes: Obj[]=[];const hashes: Value[]=[];
  for(const entry of entries) {
    const raw=binary(text(entry.content_base64)); const parsed=object(JSON.parse(decodeURIComponent(raw.map(n=>'%'+n.toString(16).padStart(2,'0')).join(''))) as Value);
    requireThat(canonical(parsed)===canonical(entry.response) && parsed.errorcode===0,'NIH_ARCHIVE_RESPONSE_MISMATCH'); envelopes.push(object(parsed.data));
    hashes.push({role:entry.role,sha256:sha256(raw),bytes:raw.length});
  }
  const [search,detail,replaySearch,replayDetail]=envelopes;
  for(const s of [search,replaySearch]) {
    const params=object(s.searchParams),hits=list(s.oppHits); const hit=object(hits[0]);
    requireThat(params.oppNum==='PA-25-301' && text(params.oppStatuses).split('|').sort().join('|')==='archived|closed|forecasted|posted' && s.hitCount===1 && s.startRecord===0 && hits.length===1 && hit.id==='357812' && hit.number==='PA-25-301' && hit.oppStatus==='posted','NIH_SELECTED_QUERY_REJECTED');
  }
  requireThat(semantic(detail)===semantic(replayDetail) && canonical(search.oppHits)===canonical(replaySearch.oppHits),'NIH_SOURCE_CHANGED_BETWEEN_READS');
  requireThat(detail.id===357812 && detail.opportunityNumber==='PA-25-301' && detail.listed==='L' && detail.ost==='POSTED' && detail.docType==='synopsis' && detail.draftMode==='N','NIH_DETAIL_IDENTITY');
  requireThat(list(detail.opportunityHistoryDetails).every(x=>object(x).opportunityId===357812 && object(x).opportunityNumber==='PA-25-301'),'NIH_HISTORY_IDENTITY');
  const synopsis=object(detail.synopsis);
  requireThat(synopsis.opportunityId===357812 && synopsis.fundingDescLinkDesc==='https://grants.nih.gov/grants/guide/pa-files/PA-25-301.html','NIH_NOFO_IDENTITY');
  const scheduleText=text(context.deadline_schedule_json),factsText=text(context.source_date_facts_json);
  const schedule=object(JSON.parse(scheduleText) as Value),facts=object(JSON.parse(factsText) as Value);
  requireThat(schedule.schema_version==='grants-deadline-schedule-v1' && schedule.Source==='us-grants-gov-nih-pa-25-301' && schedule.SourceID==='357812' && schedule.RoundID==='PA-25-301' && schedule.occurrence_count===7 && list(schedule.occurrences).length===7,'NIH_SCHEDULE_CONTEXT');
  requireThat(synopsis.responseDateStr===facts.responseDateStr && synopsis.archiveDateStr===facts.archiveDateStr && object(list(search.oppHits)[0]).closeDate===facts.search_close_date,'NIH_DATE_FACT_CHANGE_REQUIRES_ADMISSION');
  requireThat(canonical(detail.synopsisAttachmentFolders)===canonical(context.attachment_folders),'NIH_ATTACHMENT_SCOPE_CHANGED');
  const attachments=list(input.attachments).map(x=>object(x)),pins=list(context.attachment_pins).map(x=>object(x));
  requireThat(attachments.length===pins.length && pins.length===list(detail.synopsisAttachmentFolders).length,'NIH_INCOMPLETE_ATTACHMENTS');
  for(const pin of pins) { const found=attachments.filter(x=>x.folder_id===pin.folder_id);requireThat(found.length===1,'NIH_ATTACHMENT_IDENTITY'); const raw=binary(text(found[0].content_base64));requireThat(raw.length===pin.bytes && sha256(raw)===pin.sha256,'NIH_ATTACHMENT_BYTES_CHANGED');hashes.push({role:'attachment-folder-'+String(pin.folder_id),sha256:pin.sha256,bytes:pin.bytes}); }
  const raw: {[key:string]:string}={Source:'us-grants-gov-nih-pa-25-301',SourceID:'357812',RoundID:'PA-25-301',Title:text(detail.opportunityTitle),Funder:text(synopsis.agencyName),URL:text(synopsis.fundingDescLinkDesc),Description:text(synopsis.synopsisDesc),Eligibility:text(synopsis.applicantEligibilityDesc),Deadline:'',Status:'Open',RetrievedUTC:observed,DeadlineScheduleJSON:scheduleText,SourceDateFactsJSON:factsText,SourceAttribution:text(context.source_attribution)};
  for(const f of ['Title','Funder','Description','Eligibility']) requireThat(raw[f].trim().length>0,'NIH_MISSING_SOURCE_TEXT');
  requireThat(raw.SourceAttribution==='This product uses the Grants.gov API but is not endorsed or certified by the U.S. Department of Health and Human Services.','NIH_ATTRIBUTION');
  const repr='['+Object.keys(raw).sort().map(k=>'('+pyrepr(k)+', '+pyrepr(raw[k])+')').join(', ')+']';
  const row: Obj={}; for(const f of ['Title','Funder','Source','SourceID','RoundID','URL','Description','Eligibility','Status','SourceAttribution']) row[f]=normalizedText(raw[f]);
  for(const f of ['SourceRowURL','Geography','Amount','Deadline','DeadlineRaw','DeadlineTimezone','DeadlineLocalTime','DeadlineUTCInstant','DeadlineBrisbaneDate','DeadlineBrisbaneTime','Contact','ReviewNotes']) row[f]='';
  row.OpportunityKey='GRANT:'+sha256(bytes('us-grants-gov-nih-pa-25-301:357812|round:pa-25-301')).slice(0,24);
  row.Deadline=null;row.DeadlinePrecision='unknown';row.DeadlineTemporalStatus='unknown';row.DeadlineScheduleJSON=canonical(schedule);row.SourceDateFactsJSON=canonical(facts);row.CHHHSRelevance='Unknown';row.ReviewStatus='Needs Review';row.RetrievedTimestampStatus='valid';
  const parts=observed.slice(0,-1).split('.'); const micros=(parts[1]||'').padEnd(6,'0').slice(0,6);row.RetrievedUTC=parts[0]+(Number(micros)>0?'.'+micros:'')+'+00:00';row.EvidenceHash=sha256(bytes(repr));
  return JSON.stringify({format:'rims-nih-worker-v1',row:row,original_hashes:hashes,schedule_vintage_preserved:true,attachment_pin_verified:true,native_acceptance:false});
}
