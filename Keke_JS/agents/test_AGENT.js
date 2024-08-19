// BABA IS Y'ALL SOLVER - BLANK TEMPLATE
// Version 1.0
// Code by Milk 

//get imports (NODEJS)
var simjs = require('../js/simulation')					//access the game states and simulation
var astar = require('../js/astar')

let possActions = ["space", "right", "up", "left", "down"];
let doneActions = []

const stack = [];

// NEXT ITERATION STEP FOR SOLVING
function iterSolve(init_state){
	// PERFORM ITERATIVE CALCULATIONS HERE //
	//var start = graph.grid[0][0];
	//var end = graph.grid[1][2];
	//var result = astar.search(graph, start, end);
	//console.log(result)
	map = init_state.orig_map;
	//parsed_map = parseMapToAstarRequirement(map)
	
	var player = init_state.players[0];
	var winnables = init_state.winnables;
	
	if(winnables.length >= 1)
	{
		if(player === undefined)
		{
			//console.log("Player is undefined lol");
			//console.log(init_state.players);
			return ["space"];
		}
		var graphWithWeight = parseMapToAstarRequirement(init_state);
		var start = graphWithWeight.grid[player.y][player.x];
		var end = graphWithWeight.grid[winnables[0].y][winnables[0].x];
		var result = astar.astar.search(graphWithWeight, start, end);
		var movement = parseAstarResultsToInstructionlist(start, result);
	
		return movement;
	}
	else 
	{
		return ["space"];
	}
	
}

// avoiding walls, sinkables and killables
function parseMapToAstarRequirement(state) {
	map = state.orig_map;
	map_cp = state.orig_map;

	// parsing walls
	for(var i = 0; i < map.length; i++)
	{
		var row = map[i];
		for(var j = 0; j < row.length; j++)
		{
			var str = map[i][j];
			if(str == '_') {
				str = '1';
			}
			else {
				str = '0';
			}
			map_cp[i][j] = str;
		}
	}
	
	// parsing killables
	killers = state.killers
	for(var i = 0; i < killers.length; i++)
	{
		var killer = killers[i];
		map_cp[killer.y][killer.x] = '1';
	}
	
	// parsing sinkables
	sinkers = state.sinkers;
	for (var i=0; i < sinkers.length; i++)
	{
		var sinker = sinkers[i];
		map_cp[sinker.y][sinker.x] = '1';
	}
	
	var graph = new astar.Graph(map_cp);
	return graph;
}

function parseAstarResultsToInstructionlist(start, movements)
{
	result = [];
	if(movements.length <= 0)
	{
		return ["space"]
	}
	
	for(var i = 0; i < movements.length; i++)
	{
		if(i==0)
		{
			var pos_old = start;
		}
		else{
			var pos_old = movements[i-1];
		}
		
		var pos_new = movements[i];
		if (pos_old.x - pos_new.x == 1 && pos_old.y - pos_new.y == 0)
		{
			result.push("up");
		}
		else if (pos_old.x - pos_new.x == -1 && pos_old.y - pos_new.y == 0)
		{
			result.push("down");
		}
		else if (pos_old.x - pos_new.x == 0 && pos_old.y - pos_new.y == 1)
		{
			result.push("left");
		}
		else if (pos_old.x - pos_new.x == 0 && pos_old.y - pos_new.y == -1)
		{
			result.push("right");
		}
	}
	return result;
}

// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
	step : function(init_state){return iterSolve(init_state)},		// iterative step function (returns solution as list of steps from poss_actions or empty list)
	init : function(init_state){},								// initializing function here
	best_sol : function(){return [];}				//returns closest solution in case of timeout
}
