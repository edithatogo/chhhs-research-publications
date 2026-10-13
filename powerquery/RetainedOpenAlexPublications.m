// Optional typed source view; canonical publication membership stays upstream.
// Deploy alongside fnProjectRetainedOpenAlex after native archive acceptance.
let
    Observations=Table.SelectRows(RetainedSourceObservations,each [Source]="OpenAlex")
in fnProjectRetainedOpenAlex(Observations)
