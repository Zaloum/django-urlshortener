# Django Url Shortener
A url shortener implemented in Django.

<img src="https://dl.dropboxusercontent.com/s/p6n5bvnlomw1rgu/urls.png?dl=0" width="768" height="432" />

[Theme by Bootswatch](https://bootswatch.com/)

### Features
* Equivilent urls return the same shortened url 
* Canonicalizes urls
* Urls are shortened and returned without refreshing the page (using AJAX)
* Shortened urls are non-sequential
* An attempt is made to access the page and an appropriate message is returned if it is either unreachable, or has an invalid SSL cert

### Requirements
* python3
* django
* urllib3
* w3lib
* certifi

### Possible Improvements
Implement the [Google safe browsing](https://developers.google.com/safe-browsing/) API to flag potentially 'bad' sites.
