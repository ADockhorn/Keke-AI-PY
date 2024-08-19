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

let queue = [];
let allrules = [];

// Heuristics for FS 

// 1. Number Of Goals unlocked
function nbrOfGoals(state, weight=3) {
	return (weight * -Math.log(state.winnables.length));
}
// 2. Number of Players
function nbrOfPlayers(state, weight=0.1) {
	return (weight * -state.players.length);
}

// 3. Connectivity
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

//4. Out of plan - Sums the unusable words
//Can words disappear or be destroyed? If so, we could compute this at init
//Could also add different weights for IS and Suffixes
function outOfPlan(state, weight=0.5) {
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
	let leftBlocked, upBlocked, rightBlocked, belowBlocked;
	
	leftBlocked, upBlocked, rightBlocked, belowBlocked = getBlockedDirs(state, map, obj_map, x, y);
	
	// If IS is in a corner its stuck and useless
	if((leftBlocked && upBlocked) || (leftBlocked && belowBlocked) || (rightBlocked && upBlocked) || (rightBlocked && belowBlocked) )
	{
		return true;
	}
	
	return false;
}

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
	
	let leftBlocked, upBlocked, rightBlocked, belowBlocked;
	
	// Could save iterations building a new function, because right and below blocked are not needed
	leftBlocked, upBlocked, rightBlocked, belowBlocked = getBlockedDirs(state, map, obj_map, x, y);
	
	// If IS is in a corner its stuck and useless
	if(leftBlocked && upBlocked)
	{
		return true;
	}
	
	return false;
}

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
				if(!(obj_map[y][pos].type==="word"));
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
				if(!(obj_map[y][pos].type==="word"));
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
				if(!(obj_map[pos][x].type==="word"));
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
				if(!(obj_map[pos][x].type==="word"));
				{
					break;
				}
			}
		}	
	}
	return leftBlocked, upBlocked, rightBlocked, belowBlocked;
}

function elimOfAutomovers(state, weight=0.5)
{
	return (weight * state.auto_movers.length);
}
//5. Elim of Threats 
function elimOfThreats(state, weight=0.5)
{
	return (weight * state.killers.length);
}

//6. avg Distance to winnable, words and pushable
function distanceHeuristic(state, weight=0.25)
{
	if(state['players'].length == 0)
	{
		return 5000; 
	}
	else 
	{
		let win_d = heuristic2(state['players'], state['winnables']);
		let word_d = heuristic2(state['players'], state['words']);
		let push_d = heuristic2(state['players'], state['pushables']);
		
		let div = 0.000001;
		if(win_d > 0) {div++;}
		if(word_d > 0) {div++;}
		if(push_d > 0) {div++;}
		return (weight * ((win_d*4+word_d+push_d)/div));
	}
}

// 7. avg distance to killables
function distanceToKillables(state, weight=0.5)
{
	let kill_d = heuristic2(state['players'], state['killers']);
	return (weight * kill_d);
}

// 8. try to have as little different rule combinations as possible
function maximizeDifferentRules(state, weight=0.5)
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
			return weight * -20;
		}
	}
	
	
	return  0; // turns minimizing into maximizing
}

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

function findHotMelt(state)
{
	let temp = [];

	//searches rules for is-melt and is-hot
	for(const element of state.rules)
	{
		if(element.includes("is-melt"))
		{
			temp.push(element);
		}
	}

	let words = [];

	//trims the rules for the words only
	for(const element of temp)
	{
		let word1 = element.replace("-is-melt","");
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

function callAllFeaturesAndSum(state)
{
	let score = 0;
	score += nbrOfGoals(state);
	score += nbrOfPlayers(state);
	score += connectivity(state);
	score += elimOfThreats(state);
	score += distanceHeuristic(state);
	//score += distanceToKillables(state);
	//score += goalPath(state);
	score += maximizeDifferentRules(state);
	//console.log(outOfPlan(state));
	score += outOfPlan(state);
	//score += elimOfAutomovers(state);
	return score;
}

// NODE CLASS FOR EXPLORATION
function node(m, a, p, w, d){
	this.mapRep = m;
	this.actionSet = a;
	this.parent = p;
	this.win = w;
	this.died = d;
}

// CHECK IF 2 ARRAYS ARE EQUAL
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

// RESET THE QUEUE AND THE ITERATION COUNT
function initQueue(state){
	//loop until the limit is reached
	curIteration = 0;
	stateSet = [];

	//create the initial node
	let master_node = new node(simjs.map2Str(state['orig_map']), [], null, false, false);
	queue = [[0, master_node]];
	allrules = [];
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
	queue.sort();
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
			children.push(childNode);
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
	let score = callAllFeaturesAndSum(state);
	//console.log(d);
	//console.log("after KEKE (" + newActions + "): \n" + simjs.doubleMap2Str(state.obj_map, state.back_map));

	return [score, new node(maprep, newActions, parent, didwin, (state['players'].length == 0))]
}

// FIND AVERAGE DISTANCE OF GROUP THAT IS CLOSEST TO ANOTHER OBJECT IN A DIFFERENT GROUP
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

// BASIC EUCLIDEAN DISTANCE FUNCTION FROM OBJECT A TO OBJECT B
function dist(a,b){
	return (Math.abs(b.x-a.x)+Math.abs(b.y-a.y));
}

// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
	step : function(init_state){return iterSolve(init_state)},
	init : function(init_state){initQueue(init_state);},
	best_sol : function(){return (queue.length > 1 ? queue.shift()[1].actionSet : []);}
}