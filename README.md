# PartyChecker

This tool analyzes Tweets from American party officials. It also exposes an API for gathering tweets from specific users and comparing them to Twitter usage by politicians.

## Dataset

The tweets are taken from [Congressional Tweet Archive](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/BOK1CF). It is against Twitter's policy to publish a cleaned dataset with tweet text on GitHub, so in order to use this tool you will have to:

1. Download the `.xlsx` files from the above dataset
2. Export each excel sheet as a `.csv` file in the `data` folder.
	* These files should be titled `<party>-<chamber>-<congress>.csv` where 
		1. `<party>` is `democrat` or `republican`
		1. `<chamber>` is `senate` or `house`
		1. `<congress>` is `112` or `113`
	* For example, the sheet of Democrat Senator tweets from the 112th congress should be titled `democrat-senate-112.csv`
3. Run `python3 converter.py`

These steps should create a new file in the data folder called `congress-tweets.csv`, which will be used by the other scripts in this project.

## Usage

Driver code for interfacing with the tool is provided in `main.ipynb`. Running this file will process the original dataset and generate visualizations. We suggest the usage of Jupyter Notebooks to further explore the dataset.

### Comparing a Twitter user
To access Twitter's API, you need a bearer token generated from `https://developer.twitter.com`. Replace the values in `scripts/secrets.py` with your API keys and bearer tokens. 

To check the party of a twitter user, run:

`python3 checker.py <username>`