# APeurorails

This is an assistant program to the board game, Eurorails. The objective is to provide tools to assist a player in the game, from finding cities and loads to computing optimal paths between cities

## Query API
`city <list of cities>` - displays cities on map and general information in console

`load <list of loads>` - generates list of cities with specified loads

`path <list of cities>` - generates optimal path among cities (ignores owned track)
- This does the same thing as `add city ... load ...` but ignores existing track

`mission <load> <city> [all or best]` - generates path from load to city, either showing a path for each city with the load or the optimal path (ignores owned track)

`add city <list of cities> load <list of loads>` - generates paths from existing track to each city or load
- `one_major` - automatically adds all major cities (requires only one to be connected)
- `all_majors` - automatically adds all major cities (requires all to be connected)

`add mission <load> <city>` - a shorthand for `add city ... load ...` for a single mission

`remove card #` - removes specified card (by number) from stored data

`compute # # # [include_majors]` - computes the best path for the specified selection of missions and existing track.
- Mission number should be between 1 and 3, inclusive. If 0 is specified, no mission is selected for that card.
- The default option is to require a major city to be connected, but if `n` is specified at the end no major city will be included.

`compute all [y/n] [y/n] [y/n]` - computes all selections of missions for the enabled cards and existing track.
- If no parameters are specified, all mission cards are included.

`draw <path>` - draws the custom specified path using absolute and relative locations
- Can specify either exact coordinates, cities, or relative coordinates (in CCW order from right, `r, ur, ul, l, dl, dr`)

`print [log, missions]` - outputs status of saved data, depending on secondary keyword:
- `log` - outputs log history
- `missions` - outputs currently saved mission cards

`save` - saves queued track from last query to my_track and log

`clean [all]` - clears board and redraws owned track from log; `all` secondary keyword clears owned track

`undo` - removes last query from log and recomputes owned track and board from log

Notes:
- An empty query will just clear extra track.
- An asterisk after the primary keyword will save the generated track.


## Version Control

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
  - [x] Find path between multiple cities, in order of entry
  - [x] Implement history of commands so that path generation is semi-mutable
  - [x] Draw custom paths
  - [x] Remove last command
  - [x] Add mission to existing track
  - [x] Optimize path generation over missions
  - [x] Re-implement logging to only log with save option on, so that track added to mytrack is removed if not saved
  - [x] Load missions from saved missions
  - [x] Improved cost calculation on harbors in terms of travel time; should be treated as having higher cost
- Major bug fixes
  - [x] Compute costs associated with building to/from major cities correctly
  - [x] Fix mission output of best load city, which was originally set in error to the end city
  - [x] Fix output for city query, where only the first city would be outputted to console for each city

**Version 4.0.1**
- Major bug fixes
  - [x] Fixed bug where draw function didn't save because it didn't queue

### Future Versions

**Version 4.1**
- Features
  - [x] Make it possible to load queries from file

**Version 4.2**
- Features
  - [ ] Make it possible to load opponent track in game to optimize around opp. track
  - [ ] Make it possible to restrict harbors
  - [ ] Clean up README and code
  - [ ] Improve cost calculation by setting starting city
- Major bug fixes
  - [x] Fixed bug where load query would only output information on first load in list