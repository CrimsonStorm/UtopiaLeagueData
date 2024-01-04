import gspread
import copy
import pandas as pd
from google.oauth2.service_account import Credentials
import plotly.express as px
from plotly.offline import plot


def winLossRatios(data,DataToCalc):
    '''
    Loop through data to get all player names and Win-Loss rates.
    Once Win-Loss rates are obtained, store them in a list and calculate total wins, losses, and draws.
    '''
    winLossRates = []
    for x in data:
      name_to_check = x[DataToCalc]
      #print(name_to_check)
      #print(x['Win-Loss'].split('-'))
      #print(x['Win-Loss'].split('-')[0])
      
      found_indices = [index for index, sublist in enumerate(winLossRates) if name_to_check in sublist]
      if not winLossRates:
        #print("none in winlist")
        winLossRates.append([name_to_check,int(x['Win-Loss'].split('-')[0]),int(x['Win-Loss'].split('-')[1]),int(x['Win-Loss'].split('-')[2])])
        #lossList.append([name_to_check,int(x['Win-Loss'].split('-')[1])])
        #drawList.append([name_to_check,int(x['Win-Loss'].split('-')[2])])
      elif any(name_to_check in sublist for sublist in winLossRates):
        indexNum = found_indices[0]
        winLossRates[indexNum][1] += int(x['Win-Loss'].split('-')[0])
        winLossRates[indexNum][2] += int(x['Win-Loss'].split('-')[1]) 
        winLossRates[indexNum][3] += int(x['Win-Loss'].split('-')[2])
        #print("has name")
      else: 
        winLossRates.append([name_to_check,int(x['Win-Loss'].split('-')[0]),int(x['Win-Loss'].split('-')[1]),int(x['Win-Loss'].split('-')[2])])
        #lossList.append([name_to_check,int(x['Win-Loss'].split('-')[1])]) 
        #drawList.append([name_to_check,int(x['Win-Loss'].split('-')[2])])
        #print("does not have name")
    return winLossRates


def WinPercentage(winLossRatios):
  ''' 
  Calculate WinRates by looping through winLossRates from earlier.   
  Calculation is Wins/( Wins + Losses + Draws ) * 100
  ''' 
  winLossPercentages = []
  for x in winLossRatios:
    winLossPercentages.append([x[0],x[1]/ ( x[1] + x[2] + x[3] ) *100,x[2]/ ( x[1] + x[2] + x[3] ) *100])
    #print(x[0] + "'s Win Rate: " + str( x[1]/ ( x[1] + x[2] + x[3] ) *100) + '%')
  return winLossPercentages
  

# Mapping Data that will be used for plots

deck_mapping = {
    'St1 Luffy': 'Red Monkey.D.Luffy',
    'St2 Kid': 'Green Eustass "Captain" Kid',
    'St3 Crocodile': 'Blue Crocodile',
    'St4 Kaido': 'Purple Kaido',
    'OP01 Zoro': 'Red Zoro',
    'OP01 Law': 'Red /Green Trafalgar Law',
    'OP01 Luffy': 'Red/Green Monkey.D.Luffy',
    'OP01 Oden': 'Green Kouzuki Oden',
    'OP01 Doffy': 'Blue Donquixote Doflamingo',
    'OP01 Kaido': 'Blue/Purple Kaido',
    'OP01 Crocodile': 'Blue/Purple Crocodile',
    'OP01 King': 'Purple King',
    'Promo Uta': 'Red Uta',
    'St5 Shanks': 'Purple Shanks',
    'St6 Sakazuki': 'Black Sakazuki',
    'OP02 Whitebeard': 'Red Edward.Newgate',
    'OP02 Garp': 'Red/Black Monkey.D.Garp',
    'OP02 Kinemon': "Green Kin'emon",
    'OP02 Sanji': 'Green/Blue Sanji',
    'OP02 Ivankov': 'Blue Emporio.Ivankov',
    'OP02 Magellan': 'Purple Magellan',
    'OP02 Zephyr': 'Purple/Black Zephyr',
    'OP02 Smoker': 'Black Smoker',
    'St7 Big Mom': 'Yellow Charlotte Linlin',
    'OP03 Ace': 'Red Portgas.D.Ace',
    'OP03 Kuro': 'Green Kuro',
    'OP03 Arlong': 'Green/Yellow Arlong',
    'OP03 Nami': 'Blue Nami',
    'OP03 Iceburg': 'Purple Iceburg',
    'OP03 Lucci': 'Black Rob Lucci',
    'OP03 Big Mom': 'Black/Yellow Charlotte Linlin',
    'OP03 Katakuri': 'Yellow Katakuri',
    'St8 Luffy': 'Black Monkey.D.Luffy',
    'St9 Yamato': 'Yellow Yamato',
    'OP04 Nefeltari Vivi': 'Red/Blue Nefeltari Vivi',
    'OP04 Doffy': 'Green/Purple Dozuixote Doflamingo',
    'OP04 Issho': 'Green/Black Issho',
    'OP04 Rebecca': 'Blue/Black Rebecca',
    'OP04 Queen': 'Blue/Yellow Queen',
    'OP04 Crocodile': 'Purple/Yellow Crocodile',
    'St10 Law': 'Red/Purple Trafalgar Law',
    'St10 Luffy': 'Red/Purple Monkey.D.Luffy',
    'St10 Kid': 'Red/Purple Eustass "Captain" Kid',
    'OP05 Sabo': 'Red/Black Sabo',
    'OP05 Betty': 'Red/Yellow Belo Betty',
    'OP05 Rosinante': 'Green/Blue Donquixote Rosinante',
    'OP05 Sakazuki': 'Blue/Black Sakazuki',
    'OP05 Luffy': 'Purple Monkey.D.Luffy',
    'OP05 Enel': 'Yellow Enel',
    'St11 Uta': 'Green Uta',
    # Add more mappings as needed
}

# Load credentials

credentials = Credentials.from_service_account_file('utopia-one-piece-league-f149697f5d52.json', scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])


# Connect to Google Sheets

gc = gspread.authorize(credentials)


# Open the Google Sheet by its title

sheet_key = '1EKzyTHIN0fIfsrhwv9fzPMsbGpKFAItVsClrNryxUGs'
sheet = gc.open_by_key(sheet_key).sheet1


# Get data from the sheet

data = sheet.get_all_records()


# Create Plotly chart for point breakdown by player

fig = px.pie(data, names='Player_Name', values='Points_Earned')
fig.update_layout(title='Player Distribution')


# Win rates/percentages by player
'''
  Loop through data to get all player names and Win-Loss rates.
  Once Win-Loss rates are obtained, store them in a list and calculate total wins, losses, and draws.
'''

winLossRatesPlayers = winLossRatios(data,'Player_Name')
print(winLossRatesPlayers)
  
  
# Calculate Win % Per Player
 
winLossPercentages = WinPercentage(winLossRatesPlayers)
print(winLossPercentages)  

############# TODO Create Plots 



#Create Plot for Wins and losses per week for the season


# Create Plot for breakdown by leader

data3 = copy.deepcopy(data)
data3 = pd.DataFrame(data3)  # Ensure data2 is a DataFrame
data3['Deck_Used'] = data3['Deck_Used'].map(deck_mapping)
fig3 = px.pie(data, names='Deck_Used', values='Points_Earned')
fig3.update_layout(title='Leader Distribution')


# Win rates/percentages by Leader

#Note: Logic should be the same as Win/Loss Percentages by Player, but replace players with Leaders in the mapping. Refactor?
winLossRatesLeaders = winLossRatios(data,'Deck_Used')
print(winLossRatesLeaders)

# Calculate Win % Per Leader
 
winLossPercentagesLeaders = WinPercentage(winLossRatesLeaders)
print(winLossPercentagesLeaders)  


############# TODO Create Plots 


# Win rates/percentages by Color

#Note: Logic should be similar to leader win rates/percentages but separate string in the beginning to get color


############# TODO Create Plots 












'''
# Write the Plotly chart to an HTML file For Breakdown by Players
html_path = 'Breakdown_by_Player.html'

with open(html_path, 'a', encoding='utf-8') as f:
    f.write(f'<script>document.getElementById("plotContainer").innerHTML = `{fig.to_html()}`;</script>')
    
# Write the Plotly chart to an HTML file For Breakdown by Leaders

html_path = 'Breakdown_by_Leader.html'

with open(html_path, 'a', encoding='utf-8') as f:
    f.write(f'<script>document.getElementById("plotContainer").innerHTML = `{fig3.to_html()}`;</script>')
'''