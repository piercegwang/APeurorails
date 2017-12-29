# APeurorails

This is an assistant program to the board game, Eurorails. The objective is to provide tools to assist a player in the game, from finding cities and loads to computing optimal paths between cities

## Query API
`city <list of cities>` - displays cities on map and general information in console

`load <list of loads>` - generates list of cities with specified loads

`path <city 1> <city 2>` - generates optimal path between two cities

`mission <load> <city> [all or best]` - generates path from load to city, either showing a path for each city with the load or the optimal path

`addcity <list of cities>` - generates paths from each city in list to existing track

`addload <list of loads>` - generates path from each load (best path) to existing track

`save` - saves queued track

`clean [all]` - clears board and redraws owned track; `all` keyword clears owned track

## Version History

**Version 1.0**
- Features
  - [x] Query city: returns location and other information for city
  - [x] Query load: returns all cities which contain load
  - [x] Create database of cities and loads
  - [x] Implement framework for query system

**Version 1.1**
- Features
  - [x] Identify cities on map

**Version 2.0**
- Features
  - [x] Query mission: return possible paths, building cost
  - [x] Create a data representation of the board
  - [x] Display paths on map
  - [x] Query clean: erase drawings on board
  - [x] Add option to reload board
- Major bug fixes
  - [x] Fixed errors in some of the city coordinates

**Version 3.0**
- Features
  - [x] Query mission: add option to show best vs. all paths from load to city
  - [x] Create a data structure for owned track
  - [x] Query save: save track
  - [x] Query add: find best path from city to existing track
- Major bug fixes
  - [x] Change calculation of build cost to start from appropriate point
  - [x] Fix clean to allow drawing after clean is called

**Version 3.1**
- Features
  - [x] Clarify query keywords so that there is no ambiguity between cities and loads (see "cork" bug fix)
  - [x] Each query has a different randomly generated color
- Major bug fixes
  - [x] Fix ambiguity with cork as city vs. load

**Version 4.0**
- Features
  - [ ] Find best path between multiple cities
  - [x] Implement history of commands so that path generation is semi-mutable
  - [x] Draw custom paths
  - [x] Remove last command
  - [ ] Add mission to existing track
  - [ ] Optimize path generation over missions
- Major bug fixes
  - [ ] Compute costs associated with building to/from major cities correctly