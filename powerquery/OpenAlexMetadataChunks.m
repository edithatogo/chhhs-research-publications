// Frozen bootstrap only. The native owner stages the prepared JSON in the
// approved existing archive folder and binds its exact filename/input hash.
// This is a staging table, never an accepted publication/report consumer.
let
    // Reuse the exact folder reader/connection already qualified in the model.
    // Avoid another site-wide SharePoint.Files enumeration or credential binding.
    Matches=Table.SelectRows(RetainedArchiveFiles,each [Name]=pOpenAlexStagingFileName),
    Document=if Table.RowCount(Matches)=1 then Json.Document(Binary.Buffer(Matches{0}[Content]))
        else error "Missing or duplicate OpenAlex staging input",
    Rows=Document[chunks], Expected=Document[expected_keys],
    Valid=Document[kind]="openalex_retention_preparation_v1" and Document[source]="OpenAlex" and
        Document[input_sha256]=pOpenAlexInputSHA256 and Document[accepted_commit]=false and
        Document[key_column]="OpenAlexWorkID" and Document[chunk_table]="OpenAlexMetadataChunks" and
        Document[ready_for_native_stage]=true and List.Count(Expected)>0 and
        List.Count(List.Distinct(Expected))=List.Count(Expected),
    ChunkType=type table [OpenAlexWorkID=text,ChunkIndex=Int64.Type,ChunkCount=Int64.Type,
        MetadataCharacters=Int64.Type,Encoding=text,MetadataChunk=text],
    Chunks=if Valid then Table.FromRecords(Rows,ChunkType) else error "OpenAlex staging generation drift",
    // Reuse the shared decoder to reject missing/duplicate/corrupt chunks before
    // this source participates in the existing native writer's acceptance gates.
    Reconstructed=fnReconstructMetadata(Chunks,"OpenAlexWorkID"),
    ExactKeys=List.Sort(Reconstructed[SourceID])=List.Sort(Expected),
    Typed=Table.Buffer(fnProjectRetainedOpenAlex(Table.AddColumn(Reconstructed,"Source",each "OpenAlex",type text))),
    TypedCount=Table.RowCount(Typed)
in if ExactKeys and TypedCount=List.Count(Expected) then Chunks else error "OpenAlex staging keyset drift"
