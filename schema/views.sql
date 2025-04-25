CREATE VIEW finance.vw_account AS
SELECT 
    account_no, 
    account, 
    MAX(account_type) AS account_type
FROM (
    SELECT DISTINCT account_no, account, '' AS account_type 
    FROM manual_budget

    UNION ALL

    SELECT DISTINCT account_no, account, account_type 
    FROM manual_journal_entry_transaction
) temp
GROUP BY account_no, account
ORDER BY account_no, account;


CREATE VIEW finance.vw_business_unit AS
SELECT DISTINCT business_unit_id, business_unit
FROM (
    SELECT DISTINCT business_unit_id, business_unit FROM manual_budget
    UNION ALL
    SELECT DISTINCT business_unit_id, business_unit FROM manual_journal_entry_transaction
) temp
ORDER BY business_unit_id, business_unit;
