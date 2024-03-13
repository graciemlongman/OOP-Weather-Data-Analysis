import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#load in species info
species_info = pd.read_csv("data/species_info.csv", index_col = "species")

class Data:
    def __init__(self, site, species):
        """Initialise the class
        
        Parameters
        ----------
        site : str
            Site code of the location
        species : str
            Gas species
        """
        #store the site and species
        self.site = site
        self.species = species
        
        #store the path and load in the data for the specific site and species
        self.path = f"data/{site}_{species}.csv"
        self.df = pd.read_csv(self.path)
        
        #scale and units. convert to a string for a graph caption
        self.scale = str(species_info["scale"][self.species])
        self.units = str(species_info["units"][self.species])
        
        
    def __str__(self):
        """Returns f string containing appropriate data and metadata for given site and species
        """
        return f"Species: {self.species}   Site code: {self.site}    Scale: {self.scale}    Units: {self.units}"
    
    def glimpse(self):
        """Returns summary for given dataset
        """
        return self.df.describe()
    
    
    def weekly_ave(self):
        """Calculate the average mf per week for given site and species
        
        Returns
        -------
        df_ave
            df containing the weekly average mf
        """
        #weekly average calculation
        #convert time data from hourly to weekly
        self.df["week"] = pd.DatetimeIndex(self.df["time"]).to_period("W")
        
        #group by weeks then calculate mean
        df_ave = self.df.groupby(["week"]).mean()
        
        #rename "mf" column title so it is clearer and can be used as a graph title later
        df_ave.rename(columns = {"mf":"Weekly average mole fraction"}, inplace = True)
        
        return df_ave

    
    def baseline(self):
        """Calculate baseline mf using the 5th percentile over a bi-weekly window
        
        Returns
        -------
        df_ave
            Pandas data frame containing the daily average mf and the 5th percentile mf
        """
        #convert time data from hourly to daily
        self.df["day"] = pd.DatetimeIndex(self.df["time"]).to_period("D")
        
        #group by days then calculate mean
        df_ave = self.df.groupby(["day"]).mean()
        
        #calculate the 5th percentile over a 14 day window
        df_ave["Baseline"] = df_ave.rolling(14).quantile(.05)
        
        
        return df_ave.dropna() #na values are not needed
    
    
    def plot(self, data):
        """Plot specific site and species data
        Parameters
        ----------
        data: pandas series
            Data to be plotted
        """
        #store the data you want to plot
        self.data = data
        
        x = self.data.index.astype("str") #converting the index to str object
        y = self.data[self.data.columns[-1]] #indexing the last column - contains the data we want to plot
        
        title = str(self.data.columns[-1]) #take title directly from dataframe
        
        #creating the plot
        fig, ax = plt.subplots(figsize=(12,6)) #create plot and set size
        
        ax.plot(x, y, linewidth = 2, 
                color = "black", 
                label = f"{self.species}, {self.site}") #plot x and y
        
        #plotting the average mf values to compare to baseline if required
        if "Baseline" in title:
            ax.plot(x, self.data[self.data.columns[-2]], 
                    color = "seagreen", 
                    label = f"Normal {self.species} data")

        
        #setting up labels using metadata
        ax.set_title(title, fontsize = 14)     
        ax.set_ylabel(f"Mole fraction of {self.species} / {self.units} (scale:{self.scale})", fontsize = 12)
        ax.set_xlabel(f"Time ({self.data.index.year[0]})", fontsize = 12)
        
        #miscellaneous tweaks to graph
        ax.set_xticks(np.arange(0, len(y), len(y)/3.5))
        ax.grid(linestyle = "--", alpha = 0.3)
        
        plt.legend()
        plt.show()
        
        
        
    def plot_compare(self, data, other, data2): 
        """Plot specific site and species data in comparison to another
        Parameters
        ----------
        data: pandas series
            Data to be plotted
        other : Instance of Data Class
            A second instance of Data Class to plot against the first
        data2: pandas series
            Second data set to be plotted
        """
        #make sure units and scale match for appropriate comparison
        if self.units != other.units:
            raise TypeError("Units must match")

        if self.scale != other.scale:
            raise TypeError("Scale must match")
                
                
        #store the data you want to plot
        self.data = data
        other.data2 = data2
        
        #decide to use a different method to convert the index from a Period object.
        #by using .week each week in the series is numbered 1-52, i.e., returns an integer. Useful for x-axis.
        x = self.data.index.week[:-1] 
        x2 = other.data2.index.week[:-1] #can't include last value as it loops back to week 1. 
        
        y = self.data[self.data.columns[-1]][:-1] #same as above for second dataset
        y2 = other.data2[other.data2.columns[-1]][:-1]
        
        title = str(self.data.columns[-1]) #take title directly from dataframe
        
        #creating the plot
        fig, ax = plt.subplots(figsize=(12,6)) #create plot and set size
        
        #plot lines
        ax.plot(x, y, label = f"{self.species}, {self.site}", 
                color = "seagreen",
                linewidth = 2) 
        ax.plot(x2, y2, label = f"{other.species}, {other.site}", 
                color = "plum",
                linewidth = 2)
        
        #setting up labels using metadata
        ax.set_title(title, fontsize = 14)     
        ax.set_ylabel(f"Mole fraction of {self.species} / {self.units} (scale:{self.scale})", fontsize = 12)
        ax.set_xlabel(f"Weeks, {self.data.index.year[0]}", fontsize = 12)
        
        ax.grid(linestyle = "--", alpha = 0.3)
        
        plt.legend()
        plt.show()
        