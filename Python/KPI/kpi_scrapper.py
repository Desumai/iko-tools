# Automated KPI Raw data retrival from Maximo
# Requires all tabs and widgets to be fully loaded
# After all content is loaded, the body tag can be copied from 
# the Element tab in Chrome Dev Console into the exported_html.html file
# All data will be outputed into a csv file named [YYYY-MM-DD]_KPI.csv
# This is NOT intended to be a user friendly application
# scrapping html elements like this is rather fragil, generated data should be reviewed 


from bs4 import BeautifulSoup
import csv
from datetime import date

html = 'exported_html.html'
# --------------------------------
# variables to change
month = 10
year = 2020
# variables to change
# --------------------------------

with open(html, encoding='utf8', errors='ignore') as fp:
    soup = BeautifulSoup(fp, 'lxml')

sites = ['kankakee', 'sumas', 'calgary', 'sylacauga', 'hillsboro', 'hawkesbury',
'wilmington', 'ig brampton', 'bramcal', 'maximix', 'crc toronto', 'appleybridge', 'alconbury', 'madoc']

# information about tables
# [Table acronum, [table header to look for to id table], [(special operation), month / year format]]
kpis =  [
    ['MLH V KLH', ['MonthYear', 'Kronos Hours', 'Maximo Hours', 'MaximoVsKronosPercentage'], ['MM-YYYY']],
    ['LHC-LLCA', ['MonthYear', 'Labor Hours Charged to Lowest Level Child Assets', 'Total Labor Hours', "% of Labor Hours Charged To Lowest Level Child Assets"], ['MM-YYYY']],
    ['WONCP', ['MonthYear', 'Percentage'], ['MM-YYYY']],
    ['JPC', ['MonthYear', 'JobPlan Count'], ['MM-YYYY']],
    ['PMCOTT', ['PMType', 'MonthYear', 'OnTimeCount', 'Percentage'], ['MM-YYYY', 'All']],
    ['MROPRLM', ['Year', 'Month', 'MaximoPRLine', 'Mapics/JDE PRLine', '% PR Lines from Maximo'], ['YYYY', 'mm']],
    ['SWO', ['MonthYear', 'ActualNonSchedHours', 'ActualSchedHours', 'Percentage'], ['MM-YYYY']],
    ['ASPCWC', ['MonthYear', 'PriorityGroup', 'SparePartsCount'], ['SUM', 'MM-YYYY']],
    ['CC', ['MonthYear', 'No of Cycle Counts'], ['MM-YYYY']],
    ['WOFW', ['MonthYear', 'All Work Orders', 'Work Orders With First Why', 'Percentage'], ['MM-YYYY']],
]

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

#[[site], [metric], [-3 month], [-2 month], [-1 month], [report month]]
results = [['Site'], ['KPI metric'], [months[month-5]], [months[month-4]], [months[month-3]], [months[month-2]], [months[month-1]]]

for i in range(14): #loop through site pages
    site_page = soup.find(id=f"bux_iwidget_canvas_Canvas_{i}")

    # below retrives all table tags and their contents on the site's tab
    tables = [
        [
            [td.get_text(strip=True) for td in tr.find_all('td')] 
            for tr in table.find_all('tr')
        ] 
        for table in site_page.find_all('table', {"class": "ls"})
    ]

    if not tables: # if no tables can be found on the tab
        for kpi in kpis:
            results[0].append(sites[i])
            results[1].append(kpi[0])
            results[2].append('Error Tables Not Found')
            results[3].append('Error Tables Not Found')
            results[4].append('Error Tables Not Found')
            results[5].append('Error Tables Not Found')
            results[6].append('Error Tables Not Found')
        continue

    for kpi in kpis: # loop through each kpi
        results[0].append(sites[i])
        results[1].append(kpi[0])
        found_kpi = False
        for table in tables: # loop through each table on the tab
            if kpi[1] in table:
                found_kpi = True
                month_count = 2
                for j in range(month-5, month): # get current month and past 4 months of data
                    search_year = year if j > 0 else year-1
                    search = [text.replace('YYYY', str(year)).replace('MM', months[j]).replace('mm', f'0{j+1}' if j < 9 else str(j+1)) for text in kpi[2]]
                    # find and replace to generate search strings for the month & year
                    if search[0] == 'SUM': # special section for adding together the spare parts
                        search = search[1:]
                        temp = 0
                        for row in table:
                            if set(search).issubset(set(row)):
                                temp = temp + int(row[-1].replace(',' , ''))
                        results[month_count].append(temp)
                        month_count = month_count + 1
                    else: # other fields values can be found in the last column of the correct month
                        found = False
                        for row in table:
                            if set(search).issubset(set(row)):
                                results[month_count].append(row[-1])
                                month_count = month_count + 1
                                found = True
                                break
                        if not found:
                            results[month_count].append('Value Not Found for this KPI')
                            month_count = month_count + 1
        if not found_kpi: # some tables are blank even if they exist
            results[2].append('Error Tables Not Found')
            results[3].append('Error Tables Not Found')
            results[4].append('Error Tables Not Found')
            results[5].append('Error Tables Not Found')
            results[6].append('Error Tables Not Found')

with open(f'{date.today().isoformat()}_KPI.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(results)