var simjs = require('../js/simulation')

//full_biy scores
//default 61%
//weird3.0 57.6%
//weird2.0 56.5%
//weird 55.4%
//dfs 48.9%

var agentJSON = "report.json";

let possActions = ["space", "right", "up", "left", "down"];
let important_SuffixWords = ["win", "push", "you"];
let allPrefixes = ["lava", "skull", "love", "goop", "flag", "rock", "wall", "floor", "grass", "baba", "keke"];
let allSuffixes = ["stop", "sink", "push", "you", "kill", "hot", "move", "melt", "you", "win"];
let stateSet = [];

let curIteration = 0;
let allWins = [];
let nbrOfWin = 0;

let queue = [];
let allrules = [];
let unstuckWords = [];

// VARIABLES FOR TIME MEASUREMENT
let isThisTheFirstLevel = true;
let measurements = [];
let csvPath = "../../time_measurement.csv"
let levelcounter = 0;
const fs = require('fs');

// Heuristics for FS 

/**
 * Returns negative number of goals on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the negative number of goals.
 */
function nbrOfGoals(state, weight=3) {
	return (weight * -Math.log(state.winnables.length));
}

/**
 * Returns negative number of players on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the negative number of players.
 */
function nbrOfPlayers(state, weight=0.1) {
	return (weight * -state.players.length);
}

/**
 * Returns the amount of closed rooms multiplied by a weight.
 * Close Room = A closed space from which you cannot move to another room.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the amount of closed rooms.
 */
function connectivity(state, weight=2) {
	mapRes = {Map: parseRoomForConnectivityFeature(state)}; 
	var currentRooms = 0;
	var mapL = mapRes.Map.length;
	for(var i = 0; i < mapL ; i++) 
	{
		var row = mapRes.Map[i];
		var rowL = row.length;
		for(var j = 0; j < rowL; j++) 
		{
			if(mapRes.Map[i][j] === '0')
			{
				currentRooms++;
				_connectivity(mapRes, i, j, mapL, rowL);
			}
		}	
	}
	
	return  (weight * currentRooms); // turns minimizing into maximizing
}

/**
 * Returns the amount of IS-words and important Suffixes (look at variable at the beginning of this file)
 * that cannot be used to form a rule anymore, multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The IS and important suffixes that are "out of play", multiplied hy a weight.
 */
function outOfPlan(state, weight=0.25) {
	let words = state.words;
	let checking_theese_words = [];
	let counter = 0;
	let wordsinrule = state.rule_objs;
	for(const word of words)
	{
		// if the word is in the list (indexOf returns -1 if not, and first index if it is in the list)
		if(!(important_SuffixWords.indexOf(word.name)==-1))
		{
			checking_theese_words.push(word);
		}
	}
loop1:
	for(const word of checking_theese_words)
	{
loop2:
		for(const wir of wordsinrule)
		{	
			if(wir.x == word.x && wir.y == word.y)
			{
				continue loop1;
			}
		}
		if(suffixIsStuck(state, word.x, word.y))
		{
			counter++;
		}
	}

loop11:
	for(const word of state.is_connectors)
	{
loop21:
		for(const wir of wordsinrule)
		{	
			if(wir.x == word.x && wir.y == word.y)
			{
				continue loop11;
			}
		}
		if(isIsStuck(state, word.x, word.y))
		{
			counter++;
		}
	}
	return (weight * counter);
}

/**
 * Checks if an IS-word is stuck, while not being connected to a word.
 *
 * @param {object} state The current gamestate.
 * @param {number} x the x-Position of the IS-word.
 * @param {number} y the y-Position of the IS-word.
 * @return {boolean} Whether the IS-word is stuck and useless.
 */
function isIsStuck(state, x, y)
{
	let map = state.orig_map;
	let obj_map = state.obj_map;

	// Catches whether the IS is already next too a suitable word
	for(const word of state.words)
	{
		if(!(allPrefixes.indexOf(word.name)==-1))
		{
			if((word.x == x-1 && word.y == y) || (word.x == x && word.y == y-1))
			{
				return false;
			}
		}
		if(!(allSuffixes.indexOf(word.name)==-1))
		{
			if((word.x == x+1 && word.y == y) || (word.x == x && word.y == y+1))
			{
				return false;
			}
		}
	}
	let blockedDirs;
	
	blockedDirs = getBlockedDirs(state, map, obj_map, x, y);
	
	// If IS is in a corner its stuck and useless
	if((blockedDirs[0] && blockedDirs[1]) || (blockedDirs[0] && blockedDirs[3]) || (blockedDirs[2] && blockedDirs[1]) || (blockedDirs[2] && blockedDirs[3]) )
	{
		return true;
	}
	
	return false;
}

/**
 * Checks if an important Suffix (Defined list at the beginning of this File) is stuck, 
 * while not being connected to an IS-word.
 *
 * @param {object} state The current gamestate.
 * @param {number} x the x-Position of the Suffix.
 * @param {number} y the y-Position of the Suffix.
 * @return {boolean} Whether the Suffix is stuck and useless.
 */
function suffixIsStuck(state, x, y)
{
	let map = state.orig_map;
	let obj_map = state.obj_map;

	// Catches whether the Suffix is next to a suitable IS
	for(const word of state.is_connectors)
	{
		if(!(allPrefixes.indexOf(word.name)==-1))
		{
			if((word.x == x-1 && word.y == y) || (word.x == x && word.y == y-1))
			{
				return false;
			}
		}
	}
	
	let blockedDirs;
	
	// Could save iterations building a new function, because right and below blocked are not needed
	blockedDirs = getBlockedDirs(state, map, obj_map, x, y);
	
	// If IS is in a corner its stuck and useless
	if(blockedDirs[0] && blockedDirs[1])
	{
		return true;
	}
	
	return false;
}

/**
 * Checks, given a pos (x,y), for all four directions if the movement in each
 * respective direction is blocked. (not only that something is in the way, but
 * that you can't push the objects/words either)
 *
 * @param {object} state The current gamestate.
 * @param {string[]} map The current orig_map.
 * @param {object} obj_map The current object map.
 * @param {number} x the x-Position to look from.
 * @param {number} y the y-Position to look from.
 * @return {boolean[]} Is [left, up, right, down] blocked? True/False.
 */
function getBlockedDirs(state, map, obj_map, x, y)
{
	let leftBlocked, upBlocked, rightBlocked, belowBlocked;
	leftBlocked = upBlocked = rightBlocked = belowBlocked = false;
	let pos = x;
	while(true)
	{
		pos--;
		if(map[y][pos] === "_")
		{
			leftBlocked = true;
			break;
		} 
		else if(map[y][pos] === " ")
		{
			break;
		}
		else {
			if(obj_map[y][pos].is_stopped)
			{
				leftBlocked = true;
				break;
			}
			else
			{
				if(!(obj_map[y][pos].type==="word"))
				{
					break;
				}
			}
		}
	}
	pos = x;
	while(true)
	{
		pos++;
		if(map[y][pos] === "_")
		{
			rightBlocked = true;
			break;
		} 
		else if(map[y][pos] === " ")
		{
			break;
		}
		else {
			if(obj_map[y][pos].is_stopped)
			{
				rightBlocked = true;
				break;
			}
			else
			{
				if(!(obj_map[y][pos].type==="word"))
				{
					break;
				}
			}
		}
	}
	pos = y;
	while(true)
	{
		pos--;
		if(map[pos][x] === "_")
		{
			upBlocked = true;
			break;
		} 
		else if(map[pos][x] === " ")
		{
			break;
		}
		else {
			if(obj_map[pos][x].is_stopped)
			{
				upBlocked = true;
				break;
			}
			else
			{
				if(!(obj_map[pos][x].type==="word"))
				{
					break;
				}
			}
		}
	}
	pos = y;
	while(true)
	{
		pos++;
		if(map[pos][x] === "_")
		{
			belowBlocked = true;
			break;
		} 
		else if(map[pos][x] === " ")
		{
			break;
		}
		else {
			if(obj_map[pos][x].is_stopped )
			{
				belowBlocked = true;
				break;
			}
			else
			{
				if(!(obj_map[pos][x].type==="word"))
				{
					break;
				}
			}
		}	
	}
	return [leftBlocked, upBlocked, rightBlocked, belowBlocked];
}

/**
 * Returns number of auto_movers on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of automovers.
 */
function elimOfAutomovers(state, weight=0.5)
{
	return (weight * state.auto_movers.length);
}

/**
 * Returns number of killer objects on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of killers.
 */
function elimOfThreats(state, weight=0.5)
{
	return (weight * state.killers.length);
}

/**
 * Returns negative number of pushable objects on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the negative number of pushables.
 */
function maximizePushables(state, weight=0.25)
{
	return -(weight * state.pushables.length)
}

/**
 * Returns number of sinkers on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of sinkers.
 */
function minimizeSinkables(state, weight=0.25)
{
	return (weight * state.sinkers.length)
}

/**
 * Returns number of stopping objects on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of stopping objects.
 */
function minimizeStopables(state, weight=0.25)
{
	let count = 0;
	for(const object of state.phys) 
	{
		if(object.is_stopped)
		{
			count++;
		}	
	}
	return (weight * count);
}

/**
 * Calculates the average distance between the player objects and the following three groups:
 * 1. winnable objects.
 * 2. words that are not permanently locked at a position from the start.
 * 3. pushable objects.
 * And then adds theese distances up and returns them multiplied by a weight.
 * The 3 categories have different weights too.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} Average distances multiplied by a weight.
 */
function distanceHeuristic(state, weight=0.25)
{
	if(state['players'].length == 0)
	{
		return 5000; 
	}
	else 
	{
		let win_d = heuristic2(state['players'], state['winnables']);
		let word_d = heuristic2(state['players'], unstuckWords);
		let push_d = heuristic2(state['players'], state['pushables']);
		
		let div = 0.000001;
		if(win_d > 0) {div++;}
		if(word_d > 0) {div++;}
		if(push_d > 0) {div++;}
		return (weight * ((win_d*5+word_d+push_d*0.75)/div));
	}
}

/**
 * Calculates average distance from player objects to killing objects and multiplies it with a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the average distance to killing objects.
 */
function distanceToKillables(state, weight=0.25)
{
	let kill_d = heuristic2(state['players'], state['killers']);
	return (weight * kill_d);
}


/**
 * Checks the past actions for the number of times the agent stood still and multiplies this by a weight.
 * Only takes the previous actions into consideration, until the agent did something else than standing still. 
 *
 * @param {object} state The current gamestate.
 * @param {string[]} actions The past actions of the node.
 * @param (number} The weight multiplied with the average distance to killing objects.
 * @return {number} The score of standing still. 
 */
function disincentivizeStandingStill(state, actions, weight=0.1)
{
	let idleAmount = 0;
	for (let index = actions.length - 1; index >= 0; index--) {
		if(actions[index] === "space")
		{
			idleAmount++;
		}
		else 
		{
			break;
		}
	}
	return (weight * idleAmount);
}

/**
 * Tracks the amount of unique rules that where created during a level.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the amount of unique rules.
 */
 
function maximizeDifferentRules(state, weight=0.25)
{
	current_rules = state.rules;
	for(const rule of current_rules)
	{
		if(allrules.indexOf(rule) == -1)
		{
			allrules.push(rule);
		}
	}
	return (weight * allrules.length);
}

/**
 * ONLY is used on levels when there is only one WIN-word on the map. 
 * Calculates the average distance of the player objects to the only win-word,
 * and multiplies it with a weight. Is supposed to incentives the agent to move close
 * to this word.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the average distance to the only win-word.
 */
function minimizeDistanceToIsIfOnlyOneWinExists(state, weight = 0.5)
{
	if(nbrOfWin == 1)
	{
		if(state.winnables.length > 0)
		{
			return 0;
		}
		return (weight * heuristic2(state.is_connectors, allWins));
	}
	else 
	{
		return 0;
	}
}

/**
 * Helper Function for the connectivity function.
 * Recursive function that takes a parsed map and marks visited positions with a "1".
 * If neighboring positions where not visited yet, the function calls itself with said neighboring position.
 *
 * @param {string[]} map The map of the level parsed to 0s and 1s. (0=empty and not visited field 1=wall or visited field)
 * @param {number} i The current y position on the map.
 * @param {number} j The current x position on the map.
 * @param {number} mapL The maximum i dimension.
 * @param {number} rowL The maximum j dimension.
 */
function _connectivity(map, i, j, mapL, rowL) {
	map.Map[i][j] = '1';
	
	if((i+1) < mapL) {
		if(map.Map[i+1][j] === '0')
		{
			_connectivity(map, i+1, j, mapL, rowL);
		}
	}
	if((i-1) >= 0) {
		if(map.Map[i-1][j] === '0')
		{
			_connectivity(map, i-1, j, mapL, rowL);
		}
	}
	if((j+1) < rowL) {
		if(map.Map[i][j+1] === '0')
		{
			_connectivity(map, i, j+1, mapL, rowL);
		}
	}
	if((j-1) >= 0) {
		if(map.Map[i][j-1] === '0')
		{
			_connectivity(map, i, j-1, mapL, rowL);
		}
	}
}

/**
 * Parses a map in a way, that other functions like the _connectivity function can read it.
 * All walls and objects, where the player can (or shouldn't because death) not move on, are a "1".
 * All empty fields, fields with only overlappable objects, and playerfields are a "0".
 *
 * @param {object} state The current gamestate.
 * @return {string[]} The parsed map.
 */
function parseRoomForConnectivityFeature(state) 
{
	map = simjs.parseMap(simjs.showState(state));
	map_cp = JSON.parse(JSON.stringify(map))
	for(let i = 0; i < map.length; i++)
	{
		let row = map[i];
		for(let j = 0; j < row.length; j++)
		{
			let str = map[i][j];
			if(str === '_') {
				str = '1';
			}
			else {
				str = '0';
			}
			map_cp[i][j] = str;
		}
		
	}
	
	for(const killer of state.killers)
	{
		map_cp[killer.y][killer.x] = '1';
	}
	
	for(const pushable of state.pushables)
	{
		map_cp[pushable.y][pushable.x] = '1';
	}
	for(const sinker of state.sinkers)
	{
		map_cp[sinker.y][sinker.x] = '1';
	}
	
	hotmelt = findHotMelt(state);
	
	for(const hots of hotmelt)
	{
		map_cp[hots.y][hots.x] = '1';
	}
	
	for(const object of state.phys) 
	{
		if(object.is_stopped)
		{
			map_cp[object.y][object.x] = '1';
		}	
	}
	
	for(const player of state.players)
	{
		map_cp[player.y][player.x] = '0';
	}
	
	for(const winner of state.winnables)
	{
		map_cp[winner.y][winner.x] = '0';
	}
	return map_cp
}

function checkIfAllPrefixesAreStuck(state, weight=1)
{
	let prefixesInLevel = [];
	for(const word of state.words)
	{
		if(!(allPrefixes.indexOf(word.name)==-1))
		{
			let isstuck = isWordPermaStuck(state, word);
			if(!isstuck)
			{
				return 0;
			}
		}
	}
	return weight;
}
/**
 * Checks if there is a path from any player object to any winning object.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with -1 if there is a path to goal. Otherwise returns 0.
 */
function goalPath(state, weight=1) {
	mapRes = {Map: parseRoomForConnectivityFeature(state)}; 
	var currentRooms = 0;
	var mapL = mapRes.Map.length;
	var rowL = mapRes.Map[0].length;
	
	for(const player of state.players)
	{
		map_cp = JSON.parse(JSON.stringify(mapRes))
		if(_goal(map_cp, player.y, player.x, mapL, rowL, state))
		{
			return weight * -1;
		}
	}
	
	
	return  0; 
}

/**
 * Recursive helper function for the goalPath function. Works just like the _connectivity function.
 *
 * @param {string[]} map The parsed current map of the level.
 * @param {number} i The current y position on the map.
 * @param {number} j The current x position on the map.
 * @param {number} mapL The maximum i dimension.
 * @param {number} rowL The maximum j dimension.
 * @param {object} state The current gamestate.
 */
function _goal(map, i, j, mapL, rowL, state) {
	
	map.Map[i][j] = '1';
	
	for(const winner of state.winnables)
	{
		if(winner.x == j && winner.y == i)
		{
			return true;
		}
	}
	
	if((i+1) < mapL) {
		if(map.Map[i+1][j] === '0')
		{
			return _goal(map, i+1, j, mapL, rowL, state);
		}
	}
	if((i-1) >= 0) {
		if(map.Map[i-1][j] === '0')
		{
			return _goal(map, i-1, j, mapL, rowL, state);
		}
	}
	if((j+1) < rowL) {
		if(map.Map[i][j+1] === '0')
		{
			return _goal(map, i, j+1, mapL, rowL, state);
		}
	}
	if((j-1) >= 0) {
		if(map.Map[i][j-1] === '0')
		{
			return _goal(map, i, j-1, mapL, rowL, state);
		}
	}
	
	return false;
}

/**
 * Returns all objects, that are hot IF the player is melt. Otherwise just and empty list.
 *
 * @param {object} state The current gamestate.
 * @return {object[]} All objects, that are currently hot.
 */
function findHotMelt(state)
{
	let temp = [];

	//searches rules for is-melt and is-hot
	for(const element of state.rules)
	{
		if(element.includes("is-hot"))
		{
			temp.push(element);
		}
	}
	
	if(temp.length <= 0)
	{
		return temp;
	}

	let temp2 = [];
	for(const element of state.rules)
	{
		if(element.includes("is-melt"))
		{
			temp.push(element);
		}
	}
	
	if(temp2.length <= 0)
	{
		return temp2;
	}
	
	let melts = [];
	let flag = true;
	for(const element of temp)
	{
		let word1 = element.replace("-is-melt","");
		melts.push(word1);
	}
	
	for(element of state.players)
	{
		if(melts.includes(element.name))
		{
			flag = false;
			break;
		}
	}
	
	if(flag) 
	{
		return [];
	}
	
	let words = [];

	//trims the rules for the words only
	for(const element of temp)
	{
		let word1 = element.replace("-is-hot","");
		words.push(word1);
	}

	temp = [];

	//searches the objects corresponding to the words
	for(element of state.phys)
	{
		if(words.includes(element.name))
		{
			temp.push(element);
		}
	}

	return temp;
}

/**
 * Calls all heuristics that are used and sums their values together.
 *
 * @param {object} state The current gamestate.
 * @param {string[]} actions All done actions of this node. 
 * @return {number} Summed values of all heuristics.
 */
function callAllFeaturesAndSum(state, actions)
{
	let thisIterationsMeasurements = [];
	let score = 0;
	
	let start = performance.now();
	score += nbrOfGoals(state);
	let end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += nbrOfPlayers(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += connectivity(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += elimOfThreats(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += checkIfAllPrefixesAreStuck(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += maximizePushables(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += minimizeSinkables(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += distanceHeuristic(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += distanceToKillables(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += minimizeStopables(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += minimizeDistanceToIsIfOnlyOneWinExists(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += disincentivizeStandingStill(state, actions);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score += goalPath(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	start = performance.now();
	score -= maximizeDifferentRules(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	//console.log(outOfPlan(state));
	start = performance.now();
	score += outOfPlan(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	start = performance.now();
	score += elimOfAutomovers(state);
	end = performance.now();
	thisIterationsMeasurements.push((end-start));
	
	measurements.push(thisIterationsMeasurements);
	return score;
}

/**
 * Node structure used for storing visited states. Acts like a class/object.
 *
 * @param {string[]} m The map at the node state.
 * @param {string[]} a The actions done at the node state.
 * @param {object} parent The previous node.
 * @param {boolean} w Whether this node won or not. 
 * @param {object} d Whether there are no player objects or not. (dead node)
 */
function node(m, a, p, w, d){
	this.mapRep = m;
	this.actionSet = a;
	this.parent = p;
	this.win = w;
	this.died = d;
}

// Checks if two arrays are the same (not used).
function arrEq(a1,a2){
	if(a1.length != a2.length)
		return false;
	for(let a=0;a<a1.length;a++){
		if(a1[a] != a2[a])
			return false;
	}
	return true;
}

// COPIES ANYTHING NOT AN OBJECT
// DEEP COPY CODE FROM HTTPS://MEDIUM.COM/@ZIYOSHAMS/DEEP-COPYING-JAVASCRIPT-ARRAYS-4D5FC45A6E3E
function deepCopy(arr){
  let copy = [];
  arr.forEach(elem => {
    if(Array.isArray(elem)){
      copy.push(deepCopy(elem))
    }else{
      if (typeof elem === 'object') {
        copy.push(deepCopyObject(elem))
    } else {
        copy.push(elem)
      }
    }
  })
  return copy;
}

// DEEP COPY AN OBJECT
function deepCopyObject(obj){
  let tempObj = {};
  for (let [key, value] of Object.entries(obj)) {
    if (Array.isArray(value)) {
      tempObj[key] = deepCopy(value);
    } else {
      if (typeof value === 'object') {
        tempObj[key] = deepCopyObject(value);
      } else {
        tempObj[key] = value
      }
    }
  }
  return tempObj;
}

// CREATE NEW GAME STATE state AND RESET THE MAP PROPERTIES
function newstate(keke_state, m){
	simjs.clearLevel(keke_state);

	keke_state['orig_map'] = m;

	var maps = simjs.splitMap(keke_state['orig_map']);
	keke_state['back_map'] = maps[0]
	keke_state['obj_map'] = maps[1];
	
	simjs.assignMapObjs(keke_state);
	simjs.interpretRules(keke_state);
}

function calcMeanOfTimeAndWriteToCSV(){
	// Calculates average value of an Array
	const average = array => array.reduce( ( p, c ) => p + c, 0 ) / array.length;
	let addThisToCSV = "Level " + levelcounter.toString() + ",";
	for(let i = 0; i<16; i++)
	{
		// Gets column i of the measurements array and calculates its average
		let avg = average(measurements.map(function(value,index) { return value[i]; }));
		if(i != 15)
		{
			addThisToCSV += (avg.toString() + ",");
		}
		// Different ending for the last entry in the row
		else 
		{
			addThisToCSV += (avg.toString() + "\r\n");
		}
	}
	
	// Add the row to the csv file
	fs.appendFileSync(csvPath, addThisToCSV, (err) => {
			if (err) throw err;
		});
}
// RESET THE QUEUE AND THE ITERATION COUNT
function initQueue(state){
	//loop until the limit is reached
	curIteration = 0;
	stateSet = [];

	//create the initial node
	let master_node = new node(simjs.map2Str(state['orig_map']), [], null, false, false);
	queue = [[0, master_node]];
	allrules = [];
	
	//Count how many "win" words exist
	allWins = [];
	for(const word in state.words)
	{
		if(word.name === "win")
		{
			allWins.push(word);
		}
	}
	nbrOfWin = allWins.length;
	
	
	// THIS IS FOR TIME MEASUREMENT
	if(isThisTheFirstLevel) 
	{
		let data = "Level, h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16\r\n";
		isThisTheFirstLevel = false;
		fs.appendFileSync(csvPath, data, (err) => {
			if (err) throw err;
		});
	} 
	else 
	{
		calcMeanOfTimeAndWriteToCSV();
		measurements = [];
	}
	levelcounter += 1;
	//Get all words that might have changable positions
	unstuckWords = getUnstuckWords(state);
}

let count = 0;

// NEXT ITERATION STEP FOR SOLVING
function iterSolve(init_state){
	if(queue.length < 1)
		return [];

	//pop the next node off the queue and get its children
	let curnode = queue.shift()[1];
	children = getChildren(init_state['orig_map'], curnode);

	//check if golden child was found
	for(let c=0;c<children.length;c++){
		stateSet.push(children[c][1].mapRep);
		//console.log(children[c][0].mapRep);
		if(children[c][1].win){
			//console.log(children[c][1].actionSet);
			return children[c][1].actionSet;
		}
	}

	//otherwise add to the list and sort it for priority
	queue.push.apply(queue, children);
	queue.sort(function(a, b) {
		if( a[0] === Infinity ) 
			return 10000000; 
		else if( isNaN(a[0])) 
			return 10000000;
		else 
			return a[0] - b[0];
		});
	curIteration++;
	
	return [];
}

// GETS THE CHILD STATES OF A NODE
function getChildren(rootMap, parent){
	let children = [];

	for(let a=0;a<possActions.length;a++){
		//remake state everytime
		let n_kk_p = {};
		newstate(n_kk_p, rootMap)

		//let n_kk_p = deepCopyObject(rootstate);
		let childNode = getNextState([possActions[a]], n_kk_p, parent);
		
		//add if not already in the queue
		if(stateSet.indexOf(childNode[1].mapRep) == -1 && !childNode[1].died)
		{
			children.push(childNode);
		}
		//console.log(outMap);
	}
	/*
	let actionsdone = [];
	for(let i=0; i<10; i++)
	{
		// random int between 2 and 4
		let nbrOfSteps = Math.floor(Math.random() * 3) + 2;
		let actions = [];
		for(let j=0; j<nbrOfSteps; j++)
		{
			let actionnbr = Math.floor(Math.random() * 5);
			actions.push(possActions[actionnbr]);
		}
		
		let n_kk_p = {};
		newstate(n_kk_p, rootMap)

		//let n_kk_p = deepCopyObject(rootstate);
		let childNode = getNextState(actions, n_kk_p, parent);

		//add if not already in the queue
		if(stateSet.indexOf(childNode[1].mapRep) == -1 && !childNode[1].died)
			children.push(childNode);
	}*/
	
	return children;
}

// RETURNS AN ASCII REPRESENTATION OF THE MAP STATE AFTER AN ACTION IS TAKEN
function getNextState(dir, state, parent){
	//get the action space from the parent + new action
	let newActions = [];
	newActions.push.apply(newActions, parent.actionSet);
	
	for(const action of dir)
	{
		newActions.push(action);
	}

	//console.log("before KEKE (" + newActions + "): \n" + simjs.doubleMap2Str(state.obj_map, state.back_map))

	//move the along the action space
	let didwin = false;
	for(let a=0;a<newActions.length;a++){
		let res = simjs.nextMove(newActions[a],state);
		state = res['next_state'];
		didwin = res['won'];

		//everyone died
		if(state['players'].length == 0){
			didwin = false;
			break;
		}

	}
	
	// saves computation of scores when the node is already in queue.
	let maprep = simjs.doubleMap2Str(state.obj_map, state.back_map);
	if(!(stateSet.indexOf(maprep) == -1))
	{
		return [10000, new node(maprep, newActions, parent, didwin, (state['players'].length == 0))];
	}

	//return distance from nearest goal for priority queue purposes
	let score = callAllFeaturesAndSum(state, newActions);
	//console.log(d);
	//console.log("after KEKE (" + newActions + "): \n" + simjs.doubleMap2Str(state.obj_map, state.back_map));

	return [score, new node(maprep, newActions, parent, didwin, (state['players'].length == 0))]
}

/**
 * Calculates the average Distance between two groups of objects.
 *
 * @param {object[]} g1 First group of objects.
 * @param {object[]} g2 Second group of objects.
 * @return {number} Average distance between the given groups of objects.
 */
function heuristic2(g1, g2){
	let allD = [];
	for(let g=0;g<g1.length;g++){
		for(let h=0;h<g2.length;h++){
			let d = dist(g1[g], g2[h]);
			allD.push(d);
		}
	}

	let avg = 0;
	for(let i=0;i<allD.length;i++){
		avg += allD[i];
	}

	if(allD.length > 0)
	{		
		return avg/allD.length;
	}
	else
	{
		return 0;
	}
}

/**
 * Determines the closest Distance between two groups of objects.
 *
 * @param {object[]} g1 First group of objects.
 * @param {object[]} g2 Second group of objects.
 * @return {number} Closest distance between the given groups of objects.
 */
function heuristic1(g1, g2)
{
	let allD = [];
	for(let g=0;g<g1.length;g++){
		for(let h=0;h<g2.length;h++){
			let d = dist(g1[g], g2[h]);
			allD.push(d);
		}
	}
	allD.sort(function(a, b) {
		if( a[0] === Infinity ) 
			return 10000000; 
		else if( isNaN(a[0])) 
			return 10000000;
		else 
			return a[0] - b[0];
		});
	if(allD.length>0)
	{
		return allD[0];
	}
	else
	{
		return 0;
	}	
}

/**
 * Gets all words which positions are possibly not stuck.
 *
 * @param {object} state The current state of the game.
 * @return {object[]} All words that are not definatly stuck. 
 */
function getUnstuckWords(state)
{
	let result = [];
	let words = state.words;
	for(const currentword of words)
	{
		isWordStuck = isWordPermaStuck(state, currentword);
		if(!isWordStuck)
		{
			result.push(currentword);
		}
	}
	
	return result;
}

/**
 * Checks if a word is permanently stuck and cannot be moved anymore.
 *
 * @param {object} state The current state of the game.
 * @param {object} word The word that is in question.
 * @return {boolean} Whether the word is permanently stuck or not.
 */
function isWordPermaStuck(state, word)
{
	let blockedDirs;
	blockedDirs = getPermaBlockedDirs(state, state.orig_map, state.obj_map, word.x, word.y);
	
	if((blockedDirs[0] && blockedDirs[1]) || (blockedDirs[0] && blockedDirs[3]) || (blockedDirs[2] && blockedDirs[1]) || (blockedDirs[2] && blockedDirs[3]))
	{
		return true;
	}
	else 
	{
		return false;
	}
}

/**
 * Helper Function for the isWordPermaStuck function.
 * Gets the directions in which you cannot move from a certain point.
 *
 * @param {object} state The current state of the game.
 * @param {string[]} map The current orig_map of the game.
 * @param {object[]} obj_map The current obj_map of the game. 
 * @param {number} x The x position of the word in question. 
 * @param {number} y The y position of the word in question.
 * @return {boolean[]} Is [left, up, right, down] blocked? True/False.
 */
function getPermaBlockedDirs(state, map, obj_map, x, y)
{
	let leftBlocked, upBlocked, rightBlocked, belowBlocked;
	leftBlocked = upBlocked = rightBlocked = belowBlocked = false;
	let pos = x;
	while(true)
	{
		pos--;
		if(map[y][pos] === "_")
		{
			leftBlocked = true;
			break;
		} 
		else if(map[y][pos] === " ")
		{
			break;
		}
		else {
			if(!(obj_map[y][pos].type==="word"))
			{
				break;
			}
		}
	}
	pos = x;
	while(true)
	{
		pos++;
		if(map[y][pos] === "_")
		{
			rightBlocked = true;
			break;
		} 
		else if(map[y][pos] === " ")
		{
			break;
		}
		else {
			if(!(obj_map[y][pos].type==='word'))
			{
				break;
			}
		}
	}
	pos = y;
	while(true)
	{
		pos--;
		if(map[pos][x] === "_")
		{
			upBlocked = true;
			break;
		} 
		else if(map[pos][x] === " ")
		{
			break;
		}
		else {
			if(!(obj_map[pos][x].type==="word"))
			{
				break;
			}
		}
	}
	pos = y;
	while(true)
	{
		pos++;
		if(map[pos][x] === "_")
		{
			belowBlocked = true;
			break;
		} 
		else if(map[pos][x] === " ")
		{
			break;
		}
		else {
			if(!(obj_map[pos][x].type==="word"))
			{
				break;
			}
		}	
	}
	return [leftBlocked, upBlocked, rightBlocked, belowBlocked];
}

/**
 * Eukleadean Distance of Object1 to Object2
 *
 * @param {object} a The first object.
 * @param {object} b The second object.
 * @return {number} The distance from Object a to Object b.
 */
function dist(a,b){
	return (Math.abs(b.x-a.x)+Math.abs(b.y-a.y));
}

// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
	step : function(init_state){return iterSolve(init_state)},
	init : function(init_state){initQueue(init_state);},
	best_sol : function(){return (queue.length > 1 ? queue.shift()[1].actionSet : []);}
}