with source as (

    select *
    from {{ source('indohotel', 'guests') }}

),

cleaned as (

    select
        * exclude (nationality),

        case
            -- South Korea (รวม 'KOREA' เข้ากลุ่มเรียบร้อย)
            when upper(trim(nationality)) in (
                'KOREA', 'SOUTH KOREA', 'REPUBLIC OF KOREA', 'SEOUL', 'BUSAN'
            ) then 'South Korea'

            -- United States
            when upper(trim(nationality)) in (
                'USA', 'US', 'UNITED STATES', 'UNITED STATES OF AMERICA',
                'NEW YORK', 'LOS ANGELES', 'CHICAGO', 'HOUSTON', 'MIAMI',
                'GUAM', 'PUERTO RICO', 'AMERICAN SAMOA', 'US VIRGIN ISLANDS'
            ) then 'United States'

            -- United Kingdom
            when upper(trim(nationality)) in (
                'UK', 'UNITED KINGDOM', 'ENGLAND', 'SCOTLAND', 'WALES', 'NORTHERN IRELAND',
                'LONDON', 'MANCHESTER', 'EDINBURGH',
                'BERMUDA', 'CAYMAN ISLANDS', 'GIBRALTAR', 'GUERNSEY', 'JERSEY', 'ISLE OF MAN',
                'BRITISH INDIAN OCEAN TERRITORY (CHAGOS ARCHIPELAGO)'
            ) then 'United Kingdom'

            -- China
            when upper(trim(nationality)) in (
                'CHINA', 'PRC', 'BEIJING', 'SHANGHAI', 'GUANGZHOU', 'SHENZHEN',
                'HONG KONG', 'MACAO', 'MACAU'
            ) then 'China'

            -- Cote d'Ivoire / Ivory Coast
            when upper(trim(nationality)) in (
                'COTE D''IVOIRE', 'CÔTE D''IVOIRE', 'IVORY COAST'
            ) then 'Cote d''Ivoire'

            -- France
            when upper(trim(nationality)) in (
                'FRANCE', 'PARIS', 'LYON', 'MARSEILLE',
                'FRENCH POLYNESIA', 'NEW CALEDONIA', 'FRENCH GUIANA', 
                'REUNION', 'MARTINIQUE', 'GUADELOUPE', 'SAINT PIERRE AND MIQUELON'
            ) then 'France'

            -- Netherlands
            when upper(trim(nationality)) in (
                'NETHERLANDS', 'HOLLAND', 'AMSTERDAM', 'ROTTERDAM',
                'ARUBA', 'CURACAO', 'CURAÇAO', 'SINT MAARTEN', 'BONAIRE', 'NETHERLANDS ANTILLES'
            ) then 'Netherlands'

            -- Australia
            when upper(trim(nationality)) in (
                'AUSTRALIA', 'SYDNEY', 'MELBOURNE', 'BRISBANE',
                'CHRISTMAS ISLAND', 'COCOS ISLANDS', 'NORFOLK ISLAND'
            ) then 'Australia'

            -- New Zealand
            when upper(trim(nationality)) in (
                'NEW ZEALAND', 'AUCKLAND', 'WELLINGTON',
                'COOK ISLANDS', 'NIUE', 'TOKELAU'
            ) then 'New Zealand'

            -- Denmark
            when upper(trim(nationality)) in (
                'DENMARK', 'COPENHAGEN', 'GREENLAND', 'FAROE ISLANDS'
            ) then 'Denmark'

            -- Spain
            when upper(trim(nationality)) in (
                'SPAIN', 'MADRID', 'BARCELONA', 'CANARY ISLANDS'
            ) then 'Spain'

            -- Portugal
            when upper(trim(nationality)) in (
                'PORTUGAL', 'LISBON', 'PORTO', 'MADEIRA'
            ) then 'Portugal'

            -- Norway
            when upper(trim(nationality)) in (
                'NORWAY', 'OSLO', 'SVALBARD AND JAN MAYEN'
            ) then 'Norway'

            -- Finland
            when upper(trim(nationality)) in (
                'FINLAND', 'HELSINKI', 'ÅLAND ISLANDS', 'ALAND ISLANDS'
            ) then 'Finland'

            -- North Korea
            when upper(trim(nationality)) in (
                'NORTH KOREA', 'DEMOCRATIC PEOPLE''S REPUBLIC OF KOREA', 'PYONGYANG'
            ) then 'North Korea'

            -- Russia
            when upper(trim(nationality)) in (
                'RUSSIA', 'RUSSIAN FEDERATION', 'MOSCOW', 'SAINT PETERSBURG'
            ) then 'Russia'

            -- Vietnam
            when upper(trim(nationality)) in (
                'VIETNAM', 'VIET NAM', 'SOCIALIST REPUBLIC OF VIET NAM',
                'HANOI', 'HO CHI MINH', 'HO CHI MINH CITY'
            ) then 'Vietnam'

            -- Thailand
            when upper(trim(nationality)) in (
                'THAILAND', 'BANGKOK', 'CHIANG MAI', 'PHUKET'
            ) then 'Thailand'

            -- Indonesia
            when upper(trim(nationality)) in (
                'INDONESIA', 'JAKARTA', 'BALI', 'SURABAYA'
            ) then 'Indonesia'

            -- Malaysia
            when upper(trim(nationality)) in (
                'MALAYSIA', 'KUALA LUMPUR', 'PENANG'
            ) then 'Malaysia'

            -- Germany
            when upper(trim(nationality)) in (
                'GERMANY', 'BERLIN', 'MUNICH', 'FRANKFURT'
            ) then 'Germany'

            -- Italy
            when upper(trim(nationality)) in (
                'ITALY', 'ROME', 'MILAN', 'VENICE'
            ) then 'Italy'

            -- UAE
            when upper(trim(nationality)) in (
                'UAE', 'UNITED ARAB EMIRATES', 'DUBAI', 'ABU DHABI'
            ) then 'United Arab Emirates'

            -- Czech Republic
            when upper(trim(nationality)) in (
                'CZECH REPUBLIC', 'CZECHIA', 'PRAGUE'
            ) then 'Czech Republic'

            -- Slovakia
            when upper(trim(nationality)) in (
                'SLOVAKIA', 'SLOVAKIA (SLOVAK REPUBLIC)', 'BRATISLAVA'
            ) then 'Slovakia'

            -- Eswatini
            when upper(trim(nationality)) in (
                'SWAZILAND', 'ESWATINI'
            ) then 'Eswatini'

            -- Libya
            when upper(trim(nationality)) in (
                'LIBYA', 'LIBYAN ARAB JAMAHIRIYA'
            ) then 'Libya'

            -- Iran
            when upper(trim(nationality)) in (
                'IRAN', 'ISLAMIC REPUBLIC OF IRAN', 'TEHRAN'
            ) then 'Iran'

            -- Syria
            when upper(trim(nationality)) in (
                'SYRIA', 'SYRIAN ARAB REPUBLIC', 'DAMASCUS'
            ) then 'Syria'

            -- Venezuela
            when upper(trim(nationality)) in (
                'VENEZUELA', 'VENEZUELA, BOLIVARIAN REPUBLIC OF'
            ) then 'Venezuela'

            -- Bolivia
            when upper(trim(nationality)) in (
                'BOLIVIA', 'BOLIVIA, PLURINATIONAL STATE OF'
            ) then 'Bolivia'

            -- Tanzania
            when upper(trim(nationality)) in (
                'TANZANIA', 'UNITED REPUBLIC OF TANZANIA'
            ) then 'Tanzania'

            -- Moldova
            when upper(trim(nationality)) in (
                'MOLDOVA', 'REPUBLIC OF MOLDOVA'
            ) then 'Moldova'

            -- Laos
            when upper(trim(nationality)) in (
                'LAOS', 'LAO PEOPLE''S DEMOCRATIC REPUBLIC', 'VIENTIANE'
            ) then 'Laos'

            -- Myanmar
            when upper(trim(nationality)) in (
                'MYANMAR', 'BURMA', 'YANGON'
            ) then 'Myanmar'

            -- Brunei
            when upper(trim(nationality)) in (
                'BRUNEI', 'BRUNEI DARUSSALAM'
            ) then 'Brunei'

            -- Cape Verde
            when upper(trim(nationality)) in (
                'CAPE VERDE', 'CABO VERDE'
            ) then 'Cape Verde'

            -- กรณีอื่นๆ แปลงตัวแรกเป็นตัวพิมพ์ใหญ่ ตัวถัดไปเป็นตัวพิมพ์เล็ก (แก้ปัญหา initcap ไม่มีใน DuckDB)
            else upper(left(trim(nationality), 1)) || lower(substring(trim(nationality), 2))
        end as nationality,

        current_localtimestamp() as ingestion_timestamp

    from source

)

select *
from cleaned