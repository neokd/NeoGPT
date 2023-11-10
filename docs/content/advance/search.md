# __Search :mag:__

## Google API Key Configuration

!!! info "Note"
    You need to have a Google API key to use Web Research Retriever.

### Follow the steps below to get your Google API key:
1. You can find a `.env-template` file in the root directory of the repository. Rename it to `.env`.


2. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a new project.

3. If you don't have an account, you will be asked to create one and log in.

4. Create a new project by clicking on the __Select a Project__ dropdown at the top of the page and clicking __New Project__.

5. Give your project a name and click __Create__.

6. Set up a custom search API.

    1. Go to the [API and Services](https://console.cloud.google.com/apis/dashboard) page.

    2. Click on __Enable APIs and Services__.

    3. Search for __Custom Search API__ and click on it and then click __Enable__.

    4. Click on __Create Credentials__ and select __API Key__.

    5. Set is as __GOOGLE_API_KEY__ in the `.env` file.


7. Set up a custom search engine. By [Enabling](https://console.developers.google.com/apis/api/customsearch.googleapis.com).
Set up a custom search engine and add to your `.env` file.

    1. Go to the [Custom Search Engine](https://cse.google.com/cse/all) page.

    2. Click on __Add__. You can setup the search engine by following the instructions. You can set to search the entire web or only specific sites based on your needs.

    3. Once you have created the search engine, click on __Control Panel__ and then click on __Basics__. Copy the __Search engine ID__ and set it as __GOOGLE_CSE_ID__ in the `.env` file.


!!! warning "Warning"
    Avoid committing your `.env` file to the repository. It contains sensitive information.
