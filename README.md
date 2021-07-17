# Local Vicinity Entity Intersection Tool
Uses the Bing Maps API to identify locations where two categories of entities are in close proximity to each other. 

For example, finding all Shell gas stations (specific) with a sushi restaurant (nonspecific) nearby. Y'know, for those 
special, spontaneous moments in your life. 

## Bing Maps API documentation
[Local Search](https://docs.microsoft.com/en-us/bingmaps/rest-services/locations/local-search) - returns a list of 
business entities centered around a location, made by either specifying a list of types (see below) or a query.

[List of available Type Identifiers](https://docs.microsoft.com/en-us/bingmaps/rest-services/common-parameters-and-types/type-identifiers/) -
types of businesses by which you can search, e.g. `EatDrink`, `BanksAndCreditUnions`, `Hospitals`, etc.