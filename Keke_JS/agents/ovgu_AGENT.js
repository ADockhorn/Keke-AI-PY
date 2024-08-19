// BABA IS Y'ALL SOLVER - BLANK TEMPLATE
// Version 1.0
// Code by Milk 

//full_biy scores
//best submission 71.7%
//weird6.1 64.1%
//weird6.0 63.6%
//default 61%
//weird5.1 59.8%
//weird5.0 59.2%
//weird4.0 58.7%
//weird3.0 57.6%
//weird2.0 56.5%
//weird 55.4%
//dfs 48.9%

//phys_obj is_stopped = true, cannot pass through the object

//get imports (NODEJS)
var simjs = require('../js/simulation')					//access the game states and simulation

let possActions = ["space", "right", "up", "left", "down"];

var an_action_set = [];

var counter  = 0;

var currentGamestate = simjs.getGamestate();
var isYouWin = [];

//bools for earlt analysis
var WinIsSet = true;
var YouIsSet = true;

//place holder for players and winnables
var playerObject = [];
var winObject = [];

//for building the solution
var waitSequence = [];
var solveSequence = [];
var actions = [];

//filter of words which result in bad solutions
const wordFilter = ["stop", "sink", "push", "you", "kill", "hot", "move", "melt", "is", "you", "win"];

//saves the candidates for completion for every is-win combination with ascending manhattan distance
var candidatesWin = [];

//saves the win candidates for completion for every something-is combination with ascending manhattan distance
var candidatesSomething = [];

//saves the something-is combinations
var somethingIsCombinations = [];

//rules[] and rule_objs[]


/**
 * short analysis of the level to adjust the solving routine
 */
function informationHandler()
{
	//look for winnables
	if(currentGamestate.winnables.length >= 1)
	{
		winObject = currentGamestate.winnables[0];
		WinIsSet = true;
	}
	else
	{
		WinIsSet = false;
	}
	//look for players
	if(currentGamestate.players.length >= 1)
	{
		playerObject = currentGamestate.players[0];
		YouIsSet = true;
	}
	else
	{
		YouIsSet = false;
	}
}


/**
 * simple solving routine of the first step
 * in the end if plazer and winnable exist calculates the distance
 * sets the path corresponding to the distance
 */
function solution()
{
	//console.time('Execution Time');

	informationHandler();

	if(!WinIsSet || !YouIsSet)
	{
		isYouWin = isConnectorsAnalysis(currentGamestate.obj_map);

		//look for auto movers
		waitSequence = resolveAutoMove();
		//interpreteRules(currentGamestate);
	}

	let playerX = playerObject.x;
	let playerY = playerObject.y;

	let winX = winObject.x;
	let winY = winObject.y;

	difX = winX - playerX;
	difY = winY - playerY;

	actions = pathToWin(difX,difY);

	if(counter < 1)
	{
		an_action_set = an_action_set.concat(waitSequence,actions);
		counter += 1;
	}
	else
	{
		an_action_set = "Space";
	}
	//console.timeEnd('Execution Time');

	return an_action_set;
}

/**
 * analyses the object map for isYou and isWin combinations wich can be completed
 * @param {2D Array} obj_map - current object map
 * @return {2D Array} first index contains the isYou combinations, second index contains the isWin combinations
 */
function isConnectorsAnalysis(obj_map)
{
	var temp = [];

	//analyses all is combinations
	for(const element of currentGamestate.is_connectors)
	{	
		if(!(obj_map[element.y+1][element.x] === " "))
		{
			temp.push(object = 
			{name: obj_map[element.y][element.x].name.concat(obj_map[element.y+1][element.x].name),
			y: obj_map[element.y][element.x].y-1,
			x: obj_map[element.y][element.x].x,
			dir: "up"});
		}
		
		if(!(obj_map[element.y][element.x+1] === " "))
		{
			temp.push(object = 
			{name: obj_map[element.y][element.x].name.concat(obj_map[element.y][element.x+1].name),
			y: obj_map[element.y][element.x].y,
			x: obj_map[element.y][element.x].x-1,
			dir: "left"});
		}
		
		if(!(obj_map[element.y-1][element.x] === " "))
		{
			temp.push(object = 
			{name: obj_map[element.y-1][element.x].name.concat(obj_map[element.y][element.x].name),
			y: obj_map[element.y][element.x].y+1,
			x: obj_map[element.y][element.x].x,
			dir: "down"});
		}
		
		if(!(obj_map[element.y][element.x-1] === " "))
		{
			temp.push(object = 
			{name: obj_map[element.y][element.x-1].name.concat(obj_map[element.y][element.x].name),
			y: obj_map[element.y][element.x].y,
			x: obj_map[element.y][element.x].x+1,
			dir: "right"});
		}
	}

	//positions of is-you combination
	let isYou = [];

	//position of is-win combination
	let isWin = [];

	//saves combinations into different arrays, coordinates refer to the middle block
	for(const element of temp)
	{
		let newName = [];
		if(element.name === "isyou")
		{
			isYou.push(data = {y: element.y, x: element.x, dir: element.dir});
		}
		if(element.name === "iswin")
		{
			isWin.push(data = {y: element.y, x: element.x, dir: element.dir});
		}
		if(!(element.name.startsWith("is")))
		{
			somethingIsCombinations.push(data =
										{name: newName=element.name.replace("is",""),
										y: element.y,
										x: element.x,
										dir: element.dir});
		}
	}

	var output = [isYou,isWin];

	return output;
}

/**
 * looks for plausible candidates which can complete the available isWin combination
 * for each isWin combination the candidates are added in ascending order of their distances
 * in the end we obtain a 2D array where each index (isWin combination) contains an array of objects
 * @param {Object} state - current game state
 */
function isWinCompletion(state)
{
	//checks for combination of word and physics object, list of wordObjects
	let combinations = filterWordsObj(state.words);

	//words where the adjacent fields are empty
	let candidates = checkNeighbors(combinations, currentGamestate.orig_map);

	//saves suitables words to the is-win combination and sorts by ascending manhattan distance
	for(const win of isYouWin[1])
	{
		let temp = [];

		for(const candidate of candidates)
		{
			let dist = manhattanDistance(win, candidate);
			temp.push(entry = {word: candidate.name, y: candidate.y, x: candidate.x, d: dist})
		}

		temp.sort(function(a,b){return a.d - b.d});
		candidatesWin.push(temp);
	}
}

/**
 * calculates the distances of the win words to suitable somethingIs combinations as winning conditions
 * saves the win words in ascending order according to their distances for every combination
 * in the end we obtain a 2d array where each index (somethingIs combination) caontains an array of objects
 * @param {Array} somethingCombinations - array which includes all somethingIs combinations
 * @param {Object} state - current game state
 */
function SomethingIsCompletion(somethingCombinations, state)
{
	//list of word strings
	let candidates = filterString(somethingCombinations, wordFilter);

	//list of phys strings
	let possiblePhys = filterString(state.phys, wordFilter);

	//matched strings
	let filteredListWord = findCombinations(candidates, possiblePhys);

	//filtered plausable combinations
	somethingIsCombinations = filterObj(somethingCombinations, filteredListWord);

	let winWords = filterWins(state.words);

	//calculates manhattan distances to win words
	for(const element of somethingIsCombinations)
	{
		let temp = [];

		for(const win of winWords)
		{
			let dist = manhattanDistance(element, win);
			temp.push(entry = {y: win.y, x: win.x, d: dist})
		}
		temp.sort(function(a,b){return a.d - b.d});

		for(const element of temp)
		{
			candidatesSomething.push(element);
		}
	}
}


/**
 * looks out for auto movers and calculates the number of wait actions until the isYou rule is completed
 */
function resolveAutoMove()
{
	//automovers on the map
	var movers = currentGamestate.auto_movers;

	var pairsObjectiveMovers = [];

	if(movers.length < 1)
	{
		return [];
	}

	//search for combinations of automovers on the same height as isYou combinations
	for (const mover of movers)
	{
		for(const objective of isYouWin[0])
		{
			if(mover.y == objective[1])
			{
				//safe height plus x coordinates of the automover and is
				pairsObjectiveMovers.push([mover.y, mover.x, objective[0], mover.dir]);
			}
		}
	}

	var dist = 0;

	//looking for obj for completion on the the way
	for(const pair in pairsObjectiveMovers)
	{
		for(const obj in currentGamestate.obj_map[pair[0]])
		{	
			//obj hast to be between automover and is connector
			if(obj != undefined && obj.x < pair[1])
			{
				//distance is one lower because field is occupied
				dist = (pair[2] - pair[1])-1;

				//distance has to be reduced by because of pushable block
				if(pair[3] == "right")
				{
					dist -= 1;
				}
			}
		}
	}

	let output = [];

	for(let i = 0; i < dist; i += 1)
	{
		ouput.push("space");
	}
	
	/*
	if(counter < 1)
	{

	
	let print = JSON.stringify(currentGamestate.auto_movers);


	const fs = require('fs');
	fs.appendFile("../../autoMover", print, (err) => {
      
    // In case of a error throw err.
    if (err) throw err;
	});

	counter += 1;
	}
	*/

	return output;
}

/**
 * filters list of words with provided list of criterias
 * @param {Array} listToFilter - array of strings which have to be filtered
 * @param {Array} conditions - array of strings which should be excluded
 * @return {Array} array of strings (words) which are suitable
 */
function filterString(listToFilter, conditions)
{
	let temp = [];

	for(const element of listToFilter)
	{
		if(contains(element.name,conditions) || contains(element.name,temp))
		{}
		else
		{
			temp.push(element.name);
		}
	}

	return temp;
}

/**
 * keeps objects which apply to the criterias
 * @param {Array} listToFilter - array of objects which have to be filtered
 * @param {Array} conditions - array of strings which should be excluded
 * @return {Array} array of objects (phys_obj)
 */
function filterObj(listToFilter, conditions)
{
	let temp = [];

	for(const element of listToFilter)
	{
		if(contains(element.name,conditions))
		{
			temp.push(element);
		}
		else
		{}
	}

	return temp;
}

/**
 * filters array of objects for win objects
 * @param {Array} mapWords - array of objects which have to be filtered
 * @return {Array} array of win objects (phys_obj) with their coordinates
 */
function filterWins(mapWords)
{
	let temp = [];

	for(const element of mapWords)
	{
		if(element.name === "win")
		{
			temp.push(data = {y: element.y, x: element.x});
		}
	}

	return temp;
}

/**
 * filters array of words if word in the list has also a phys object
 * @param {Array} wordsList - array of objects which have to be filtered
 * @return {Array} array of word objects which have a phys object as well
 */
function filterWordsObj(wordsList)
{
	let temp = [];

	for(const word of wordsList)
	{
		if(word.obj !== undefined)
		{
			temp.push(word);
		}
	}

	return temp;
}

/**
 * filters array of objects for win objects
 * @param {Array} stringListWord - array of strings of the filtered words
 * @param {Array} stringListPhys - array of strings of the filtered objects
 * @return {Array} array of strings where combination of word and phys object exists
 */
function findCombinations(stringListWord, stringListPhys)
{
	let temp = [];

	for(const word of stringListWord)
	{
		for(const phys of stringListPhys)
		{
			if((word === phys) && !(contains(word,temp)))
			{
				temp.push(word);
			}
		}
	}

	return temp;
}

//returns array of hot and melt objects with position, includes player objects as well

/**
 * filters for hot and melt objects, includes player objects as well
 * @param {Object} state - current game state
 * @return {Array} array of hot and melt objects
 */
function findHotMelt(state)
{
	let temp = [];

	//searches rules for is-melt and is-hot
	for(const element of state.rules)
	{
		if(element.includes("is-melt") || element.includes("is-hot"))
		{
			temp.push(element);
		}
	}

	let words = [];

	//trims the rules for the words only
	for(const element of temp)
	{
		let word1 = element.replace("-is-melt","");
		let word2 = word1.replace("-is-hot","");
		words.push(word2);
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
 * look if an element is included in a data structure
 * @param {string} subject - string which has to be reviewed
 * @param {Array} data - array of strings which should be compared
 * @return {boolean} true if subject is included
 */
function contains(subject, data)
{
	for(const element of data)
	{
		if(element === subject)
		{
			return true;
		}
	}

	return false;
}

//check neighbors of a list of words, returns list of words where adjacent fields are empty

/**
 * check neighbors of the candidates
 * @param {Array} candidates - array of word objects
 * @param {2D Array} map - map representation of the current game state
 * @return {Array} array of words which could be accessed
 */
function checkNeighbors(candidates, map)
{
	let temp = [];

	for(const word of candidates)
	{
		let checker = false;
		if(((map[word.y][word.x+1] === " ") && (map[word.y][word.x-1] === " "))||((map[word.y-1][word.x] === " ") && (map[word.y+1][word.x] === " "))){ checker = true;}

		if(checker){ temp.push(word);}
	}

	return temp;
}

/**
 * calculates manhatten distance between two points
 * @param {Object} point1 - object with x and y member
 * @param {Object} point2 - object with x and y member
 * @return {int} manhattan distance between th etwo points
 */
function manhattanDistance(point1, point2)
{
	let difY = point1.y - point2.y;
	let difX = point1.x - point2.x;

	return Math.abs(difY) + Math.abs(difX);
}
/**
 * calculates manhatten distance between two points
 * @param {int} x - movment in x
 * @param {int} y - movment in y
 * @return {Array} array of strings which represents the path which has to be taken
 */
function pathToWin(x,y)
{
	let path = [];
	for(let i = 0; i < Math.abs(x); i +=1)
	{
		if(x < 0)
		{
			path.push("left");
		}
		else
		{
			path.push("right");
		}
	}
	
	for(let i = 0; i < Math.abs(y); i += 1)
	{
		if(y < 0)
		{
			path.push("up");
		}
		else
		{
			path.push("down");
		}
	}	

	return path;
}

// NEXT ITERATION STEP FOR SOLVING
function iterSolve(init_state)
{
	// PERFORM ITERATIVE CALCULATIONS HERE //
	/*
	if(counter < 1)
	{
		isYouWin = isConnectorsAnalysis(init_state.obj_map);
		SomethingIsCompletion(somethingIsCombinations, init_state);
		//console.log(output);

	
	data = "TryHard, 13, 42, Do not look at me\r\n";

	const fs = require('fs');
	fs.appendFileSync("../../output.csv", data, (err) => {
      
    // In case of a error throw err.
    if (err) throw err;
	});

	//counter += 1;
	//}
	*/

	//return a sequence of actions or empty list
	return solution();
}

// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
	step : function(init_state){return iterSolve(init_state)},		// iterative step function (returns solution as list of steps from poss_actions or empty list)
	init : function(init_state){},									// initializing function here
	best_sol : function(){return an_action_set;}
}