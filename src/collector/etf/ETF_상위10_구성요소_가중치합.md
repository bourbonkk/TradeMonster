```sql
SELECT etf_id|
    SUM(weight_percentage) AS total_weight
FROM
    etf_components
GROUP BY
    etf_id
ORDER BY
    etf_id;
```

| etf_id                          | top10_total_weight |
|---------------------------------|--------------------|
| SPDR Select Sector Fund - Techn | 0.6125             |
| VanEck Semiconductor ETF        | 0.7207             |
| SPDR Select Sector Fund - Finan | 0.5613             |
| SPDR S&P Bank ETF               | 0.1186             |
| SPDR Select Sector Fund - Healt | 0.5681             |
| iShares Biotechnology ETF       | 0.4984             |
| SPDR Select Sector Fund - Consu | 0.6195             |
| SPDR Select Sector Fund - Consu | 0.6879             |
| The Communication Services Sele | 0.6537             |
| SPDR Select Sector Fund - Indus | 0.3622             |
| First Trust S-Network Electric  | 0.4454             |
| SPDR Select Sector Fund - Energ | 0.7403             |
| Materials Select Sector SPDR    | 0.6274             |
| SPDR Select Sector Fund - Utili | 0.5637             |
| Real Estate Select Sector SPDR  | 0.6154             |
