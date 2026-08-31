with source as (

    select *
    from {{ source('indohotel', 'guests') }}

),

cleaned as (

    select
        * exclude (nationality),

        case

            /* =====================================================
               1. SOUTH KOREA
               ===================================================== */
            when upper(trim(nationality)) in (
                'KOREA',
                'SOUTH KOREA',
                'REPUBLIC OF KOREA',
                'SEOUL',
                'BUSAN'
            ) then 'South Korea'


            /* =====================================================
               2. NORTH KOREA
               ===================================================== */
            when upper(trim(nationality)) in (
                'NORTH KOREA',
                'DEMOCRATIC PEOPLE''S REPUBLIC OF KOREA',
                'PYONGYANG'
            ) then 'North Korea'


            /* =====================================================
               3. UNITED STATES
               ===================================================== */
            when upper(trim(nationality)) in (
                'USA',
                'US',
                'UNITED STATES',
                'UNITED STATES OF AMERICA',
                'NEW YORK',
                'LOS ANGELES',
                'CHICAGO',
                'HOUSTON',
                'MIAMI',
                'GUAM',
                'PUERTO RICO',
                'AMERICAN SAMOA',
                'US VIRGIN ISLANDS',
                'UNITED STATES VIRGIN ISLANDS',
                'UNITED STATES MINOR OUTLYING ISLANDS',
                'NORTHERN MARIANA ISLANDS'
            ) then 'United States'


            /* =====================================================
               4. UNITED KINGDOM
               ===================================================== */
            when upper(trim(nationality)) in (
                'UK',
                'UNITED KINGDOM',
                'ENGLAND',
                'SCOTLAND',
                'WALES',
                'NORTHERN IRELAND',
                'LONDON',
                'MANCHESTER',
                'EDINBURGH',
                'BERMUDA',
                'CAYMAN ISLANDS',
                'GIBRALTAR',
                'GUERNSEY',
                'JERSEY',
                'ISLE OF MAN',
                'BRITISH INDIAN OCEAN TERRITORY (CHAGOS ARCHIPELAGO)'
            ) then 'United Kingdom'


            /* =====================================================
               5. CHINA
               ===================================================== */
            when upper(trim(nationality)) in (
                'CHINA',
                'PRC',
                'BEIJING',
                'SHANGHAI',
                'GUANGZHOU',
                'SHENZHEN',
                'HONG KONG',
                'MACAO',
                'MACAU'
            ) then 'China'


            /* =====================================================
               6. CÔTE D'IVOIRE
               ===================================================== */
            when upper(trim(nationality)) in (
                'COTE D''IVOIRE',
                'CÔTE D''IVOIRE',
                'IVORY COAST'
            ) then 'Côte d''Ivoire'


            /* =====================================================
               7. FRANCE
               ===================================================== */
            when upper(trim(nationality)) in (
                'FRANCE',
                'PARIS',
                'LYON',
                'MARSEILLE',
                'FRENCH POLYNESIA',
                'NEW CALEDONIA',
                'FRENCH GUIANA',
                'REUNION',
                'MARTINIQUE',
                'GUADELOUPE',
                'SAINT PIERRE AND MIQUELON',
                'FRENCH SOUTHERN TERRITORIES',
                'MAYOTTE',
                'WALLIS AND FUTUNA',
                'SAINT BARTHELEMY'
            ) then 'France'


            /* =====================================================
               8. NETHERLANDS
               ===================================================== */
            when upper(trim(nationality)) in (
                'NETHERLANDS',
                'HOLLAND',
                'AMSTERDAM',
                'ROTTERDAM',
                'ARUBA',
                'CURACAO',
                'CURAÇAO',
                'SINT MAARTEN',
                'BONAIRE',
                'NETHERLANDS ANTILLES'
            ) then 'Netherlands'


            /* =====================================================
               9. AUSTRALIA
               ===================================================== */
            when upper(trim(nationality)) in (
                'AUSTRALIA',
                'SYDNEY',
                'MELBOURNE',
                'BRISBANE',
                'CHRISTMAS ISLAND',
                'COCOS ISLANDS',
                'COCOS (KEELING) ISLANDS',
                'NORFOLK ISLAND',
                'HEARD ISLAND AND MCDONALD ISLANDS'
            ) then 'Australia'


            /* =====================================================
               10. NEW ZEALAND
               ===================================================== */
            when upper(trim(nationality)) in (
                'NEW ZEALAND',
                'AUCKLAND',
                'WELLINGTON',
                'COOK ISLANDS',
                'NIUE',
                'TOKELAU'
            ) then 'New Zealand'


            /* =====================================================
               11. DENMARK
               ===================================================== */
            when upper(trim(nationality)) in (
                'DENMARK',
                'COPENHAGEN',
                'GREENLAND',
                'FAROE ISLANDS'
            ) then 'Denmark'


            /* =====================================================
               12. SPAIN
               ===================================================== */
            when upper(trim(nationality)) in (
                'SPAIN',
                'MADRID',
                'BARCELONA',
                'CANARY ISLANDS'
            ) then 'Spain'


            /* =====================================================
               13. PORTUGAL
               ===================================================== */
            when upper(trim(nationality)) in (
                'PORTUGAL',
                'LISBON',
                'PORTO',
                'MADEIRA'
            ) then 'Portugal'


            /* =====================================================
               14. NORWAY
               ===================================================== */
            when upper(trim(nationality)) in (
                'NORWAY',
                'OSLO',
                'SVALBARD AND JAN MAYEN',
                'SVALBARD & JAN MAYEN ISLANDS',
                'BOUVET ISLAND (BOUVETOYA)'
            ) then 'Norway'


            /* =====================================================
               15. FINLAND
               ===================================================== */
            when upper(trim(nationality)) in (
                'FINLAND',
                'HELSINKI',
                'ÅLAND ISLANDS',
                'ALAND ISLANDS'
            ) then 'Finland'


            /* =====================================================
               16. RUSSIA
               ===================================================== */
            when upper(trim(nationality)) in (
                'RUSSIA',
                'RUSSIAN FEDERATION',
                'MOSCOW',
                'SAINT PETERSBURG'
            ) then 'Russia'


            /* =====================================================
               17. VIETNAM
               ===================================================== */
            when upper(trim(nationality)) in (
                'VIETNAM',
                'VIET NAM',
                'SOCIALIST REPUBLIC OF VIET NAM',
                'HANOI',
                'HO CHI MINH',
                'HO CHI MINH CITY'
            ) then 'Vietnam'


            /* =====================================================
               18. THAILAND
               ===================================================== */
            when upper(trim(nationality)) in (
                'THAILAND',
                'BANGKOK',
                'CHIANG MAI',
                'PHUKET'
            ) then 'Thailand'


            /* =====================================================
               19. INDONESIA
               ===================================================== */
            when upper(trim(nationality)) in (
                'INDONESIA',
                'JAKARTA',
                'BALI',
                'SURABAYA'
            ) then 'Indonesia'


            /* =====================================================
               20. MALAYSIA
               ===================================================== */
            when upper(trim(nationality)) in (
                'MALAYSIA',
                'KUALA LUMPUR',
                'PENANG'
            ) then 'Malaysia'


            /* =====================================================
               21. GERMANY
               ===================================================== */
            when upper(trim(nationality)) in (
                'GERMANY',
                'BERLIN',
                'MUNICH',
                'FRANKFURT'
            ) then 'Germany'


            /* =====================================================
               22. ITALY
               ===================================================== */
            when upper(trim(nationality)) in (
                'ITALY',
                'ROME',
                'MILAN',
                'VENICE'
            ) then 'Italy'


            /* =====================================================
               23. UNITED ARAB EMIRATES
               ===================================================== */
            when upper(trim(nationality)) in (
                'UAE',
                'UNITED ARAB EMIRATES',
                'DUBAI',
                'ABU DHABI'
            ) then 'United Arab Emirates'


            /* =====================================================
               24. CZECHIA
               ===================================================== */
            when upper(trim(nationality)) in (
                'CZECH REPUBLIC',
                'CZECHIA',
                'PRAGUE'
            ) then 'Czechia'


            /* =====================================================
               25. SLOVAKIA
               ===================================================== */
            when upper(trim(nationality)) in (
                'SLOVAKIA',
                'SLOVAKIA (SLOVAK REPUBLIC)',
                'BRATISLAVA'
            ) then 'Slovakia'


            /* =====================================================
               26. ESWATINI
               ===================================================== */
            when upper(trim(nationality)) in (
                'SWAZILAND',
                'ESWATINI'
            ) then 'Eswatini'


            /* =====================================================
               27. LIBYA
               ===================================================== */
            when upper(trim(nationality)) in (
                'LIBYA',
                'LIBYAN ARAB JAMAHIRIYA'
            ) then 'Libya'


            /* =====================================================
               28. IRAN
               ===================================================== */
            when upper(trim(nationality)) in (
                'IRAN',
                'ISLAMIC REPUBLIC OF IRAN',
                'TEHRAN'
            ) then 'Iran'


            /* =====================================================
               29. SYRIA
               ===================================================== */
            when upper(trim(nationality)) in (
                'SYRIA',
                'SYRIAN ARAB REPUBLIC',
                'DAMASCUS'
            ) then 'Syria'


            /* =====================================================
               30. VENEZUELA
               ===================================================== */
            when upper(trim(nationality)) in (
                'VENEZUELA',
                'VENEZUELA, BOLIVARIAN REPUBLIC OF'
            ) then 'Venezuela'


            /* =====================================================
               31. BOLIVIA
               ===================================================== */
            when upper(trim(nationality)) in (
                'BOLIVIA',
                'BOLIVIA, PLURINATIONAL STATE OF'
            ) then 'Bolivia'


            /* =====================================================
               32. TANZANIA
               ===================================================== */
            when upper(trim(nationality)) in (
                'TANZANIA',
                'UNITED REPUBLIC OF TANZANIA'
            ) then 'Tanzania'


            /* =====================================================
               33. MOLDOVA
               ===================================================== */
            when upper(trim(nationality)) in (
                'MOLDOVA',
                'REPUBLIC OF MOLDOVA'
            ) then 'Moldova'


            /* =====================================================
               34. LAOS
               ===================================================== */
            when upper(trim(nationality)) in (
                'LAOS',
                'LAO PEOPLE''S DEMOCRATIC REPUBLIC',
                'VIENTIANE'
            ) then 'Laos'


            /* =====================================================
               35. MYANMAR
               ===================================================== */
            when upper(trim(nationality)) in (
                'MYANMAR',
                'BURMA',
                'YANGON'
            ) then 'Myanmar'


            /* =====================================================
               36. BRUNEI
               ===================================================== */
            when upper(trim(nationality)) in (
                'BRUNEI',
                'BRUNEI DARUSSALAM'
            ) then 'Brunei'


            /* =====================================================
               37. CAPE VERDE
               ===================================================== */
            when upper(trim(nationality)) in (
                'CAPE VERDE',
                'CABO VERDE'
            ) then 'Cape Verde'


            /* =====================================================
               38. OTHER COUNTRIES / STANDARD COUNTRY NAMES
               เพิ่มประเทศที่เป็นชื่อประเทศอยู่แล้ว
               ===================================================== */

            when upper(trim(nationality)) = 'AFGHANISTAN'
                then 'Afghanistan'

            when upper(trim(nationality)) = 'ALBANIA'
                then 'Albania'

            when upper(trim(nationality)) = 'ALGERIA'
                then 'Algeria'

            when upper(trim(nationality)) = 'ARGENTINA'
                then 'Argentina'

            when upper(trim(nationality)) = 'ARMENIA'
                then 'Armenia'

            when upper(trim(nationality)) = 'AUSTRIA'
                then 'Austria'

            when upper(trim(nationality)) = 'AZERBAIJAN'
                then 'Azerbaijan'

            when upper(trim(nationality)) = 'BAHRAIN'
                then 'Bahrain'

            when upper(trim(nationality)) = 'BANGLADESH'
                then 'Bangladesh'

            when upper(trim(nationality)) = 'BELARUS'
                then 'Belarus'

            when upper(trim(nationality)) = 'BELGIUM'
                then 'Belgium'

            when upper(trim(nationality)) = 'BELIZE'
                then 'Belize'

            when upper(trim(nationality)) = 'BHUTAN'
                then 'Bhutan'

            when upper(trim(nationality)) = 'BRAZIL'
                then 'Brazil'

            when upper(trim(nationality)) = 'BULGARIA'
                then 'Bulgaria'

            when upper(trim(nationality)) = 'CAMBODIA'
                then 'Cambodia'

            when upper(trim(nationality)) = 'CAMEROON'
                then 'Cameroon'

            when upper(trim(nationality)) = 'CANADA'
                then 'Canada'

            when upper(trim(nationality)) = 'CHILE'
                then 'Chile'

            when upper(trim(nationality)) = 'COLOMBIA'
                then 'Colombia'

            when upper(trim(nationality)) = 'COSTA RICA'
                then 'Costa Rica'

            when upper(trim(nationality)) = 'CROATIA'
                then 'Croatia'

            when upper(trim(nationality)) = 'CYPRUS'
                then 'Cyprus'

            when upper(trim(nationality)) = 'ECUADOR'
                then 'Ecuador'

            when upper(trim(nationality)) = 'EGYPT'
                then 'Egypt'

            when upper(trim(nationality)) = 'ESTONIA'
                then 'Estonia'

            when upper(trim(nationality)) = 'ETHIOPIA'
                then 'Ethiopia'

            when upper(trim(nationality)) = 'GREECE'
                then 'Greece'

            when upper(trim(nationality)) = 'HUNGARY'
                then 'Hungary'

            when upper(trim(nationality)) = 'ICELAND'
                then 'Iceland'

            when upper(trim(nationality)) = 'INDIA'
                then 'India'

            when upper(trim(nationality)) = 'IRELAND'
                then 'Ireland'

            when upper(trim(nationality)) = 'ISRAEL'
                then 'Israel'

            when upper(trim(nationality)) = 'JAPAN'
                then 'Japan'

            when upper(trim(nationality)) = 'JORDAN'
                then 'Jordan'

            when upper(trim(nationality)) = 'KAZAKHSTAN'
                then 'Kazakhstan'

            when upper(trim(nationality)) = 'KENYA'
                then 'Kenya'

            when upper(trim(nationality)) = 'KUWAIT'
                then 'Kuwait'

            when upper(trim(nationality)) = 'LATVIA'
                then 'Latvia'

            when upper(trim(nationality)) = 'LEBANON'
                then 'Lebanon'

            when upper(trim(nationality)) = 'LITHUANIA'
                then 'Lithuania'

            when upper(trim(nationality)) = 'LUXEMBOURG'
                then 'Luxembourg'

            when upper(trim(nationality)) = 'MALDIVES'
                then 'Maldives'

            when upper(trim(nationality)) = 'MALTA'
                then 'Malta'

            when upper(trim(nationality)) = 'MAURITIUS'
                then 'Mauritius'

            when upper(trim(nationality)) = 'MEXICO'
                then 'Mexico'

            when upper(trim(nationality)) = 'MONGOLIA'
                then 'Mongolia'

            when upper(trim(nationality)) = 'MOROCCO'
                then 'Morocco'

            when upper(trim(nationality)) = 'NEPAL'
                then 'Nepal'

            when upper(trim(nationality)) = 'NIGERIA'
                then 'Nigeria'

            when upper(trim(nationality)) = 'PAKISTAN'
                then 'Pakistan'

            when upper(trim(nationality)) = 'PANAMA'
                then 'Panama'

            when upper(trim(nationality)) = 'PARAGUAY'
                then 'Paraguay'

            when upper(trim(nationality)) = 'PERU'
                then 'Peru'

            when upper(trim(nationality)) = 'PHILIPPINES'
                then 'Philippines'

            when upper(trim(nationality)) = 'POLAND'
                then 'Poland'

            when upper(trim(nationality)) = 'ROMANIA'
                then 'Romania'

            when upper(trim(nationality)) = 'SAUDI ARABIA'
                then 'Saudi Arabia'

            when upper(trim(nationality)) = 'SERBIA'
                then 'Serbia'

            when upper(trim(nationality)) = 'SINGAPORE'
                then 'Singapore'

            when upper(trim(nationality)) = 'SLOVENIA'
                then 'Slovenia'

            when upper(trim(nationality)) = 'SOUTH AFRICA'
                then 'South Africa'

            when upper(trim(nationality)) = 'SRI LANKA'
                then 'Sri Lanka'

            when upper(trim(nationality)) = 'SWEDEN'
                then 'Sweden'

            when upper(trim(nationality)) = 'SWITZERLAND'
                then 'Switzerland'

            when upper(trim(nationality)) = 'TUNISIA'
                then 'Tunisia'

            when upper(trim(nationality)) = 'UKRAINE'
                then 'Ukraine'

            when upper(trim(nationality)) = 'URUGUAY'
                then 'Uruguay'

            when upper(trim(nationality)) = 'UZBEKISTAN'
                then 'Uzbekistan'

            when upper(trim(nationality)) = 'ZAMBIA'
                then 'Zambia'

            when upper(trim(nationality)) = 'ZIMBABWE'
                then 'Zimbabwe'


            /* =====================================================
               39. AMBIGUOUS / TERRITORIES
               → Others
               ===================================================== */

            when upper(trim(nationality)) in (
                'CONGO',
                'SAINT MARTIN',
                'WESTERN SAHARA',
                'PALESTINIAN TERRITORY',
                'TAIWAN',
                'ANTARCTICA (THE TERRITORY SOUTH OF 60 DEG S)',
                'BRITISH VIRGIN ISLANDS',
                'ANGUILLA',
                'MONTSERRAT',
                'PITCAIRN ISLANDS',
                'SAINT HELENA',
                'TURKS AND CAICOS ISLANDS'
            ) then 'Others'


            /* =====================================================
               40. NULL / EMPTY
               ===================================================== */

            when nationality is null
                then 'Others'

            when trim(nationality) = ''
                then 'Others'


            /* =====================================================
               41. EVERYTHING ELSE
               ===================================================== */

            else 'Others'

        end as nationality,

        current_localtimestamp() as ingestion_timestamp

    from source

)
<<<<<<< HEAD
select
    *,
    current_timestamp() as ingestion_timestamp
from source
=======

select *
from cleaned
>>>>>>> hotel
