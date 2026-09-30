let
    // Replace with your completed analysis output folder, including the final slash.
    Folder = "C:\path\to\analysis\output\202607\",
    ReadCsv = (Name as text) as table =>
        let
            Raw = Csv.Document(File.Contents(Folder & Name), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            Headers = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),
            Blanks = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers))
        in Blanks,
    Overview = Table.TransformColumnTypes(ReadCsv("01_monthly_overview.csv"), {
        {"month", type text}, {"records", Int64.Type},
        {"observed_organisations", Int64.Type}, {"observed_products", Int64.Type},
        {"known_cost_records", Int64.Type}, {"missing_cost_records", Int64.Type},
        {"invalid_cost_records", Int64.Type}, {"known_cost_record_percent", type number},
        {"known_net_indicative_cost_gbp", type number}
    }, "en-GB"),
    Sensitivity = Table.TransformColumnTypes(ReadCsv("05_cost_sensitivity.csv"), {
        {"month", type text}, {"records", Int64.Type},
        {"negative_cost_records", Int64.Type}, {"nonnegative_only_cost_gbp", type number},
        {"negative_component_gbp", type number}
    }, "en-GB"),
    UniqueMonths = Table.RowCount(Table.Distinct(Overview, {"month"})) = Table.RowCount(Overview)
        and Table.RowCount(Table.Distinct(Sensitivity, {"month"})) = Table.RowCount(Sensitivity),
    Joined = if not UniqueMonths then error "Duplicate month summaries; use one completed analysis run."
        else Table.NestedJoin(Overview, {"month"}, Sensitivity, {"month"}, "CostScenario", JoinKind.LeftOuter),
    Checked = if Table.RowCount(Overview) <> Table.RowCount(Sensitivity)
        or List.AnyTrue(List.Transform(Joined[CostScenario], each Table.RowCount(_) <> 1))
        then error "Monthly summaries do not match. Use files from the same completed run."
        else Joined,
    Expanded = Table.ExpandTableColumn(Checked, "CostScenario",
        {"records", "negative_cost_records", "nonnegative_only_cost_gbp", "negative_component_gbp"},
        {"scenario_records", "negative_cost_records", "nonnegative_only_cost_gbp", "negative_component_gbp"}),
    Reconciled = if Table.RowCount(Table.SelectRows(Expanded, each [records] <> [scenario_records])) > 0
        then error "Record counts differ between summaries." else Expanded,
    Result = Table.RemoveColumns(Reconciled, {"scenario_records"})
in
    Result
