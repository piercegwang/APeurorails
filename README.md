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