
// BABA IS Y'ALL SOLVER - BLANK TEMPLATE
// Version 1.0
// Code by Max 


//get imports (NODEJS)
var simjs = require('../js/simulation')					//access the game states and simulation

let possActions = ["space", "right", "up", "left", "down"];

function GivenextAction(DeadlyAction){
	let iterator = 0;
	while(!(DeadlyAction===possActions[iterator])){
		iterator++;
//		console.log("iterator",iterator)

	}
//	console.log("iterator",iterator)
	if(iterator==4){return possActions[0]}
//	console.log("iterator",iterator)
	return possActions[iterator+1];

}
const stateSet = new Set();
const stack = [];

//Class for exploration and already walked Path
class Node {
  constructor(m, a, p, w, d) {
    this.mapRep = m;
    this.actionHistory = a;
    this.parent = p;
    this.won = w;
    this.died = d;
  }
}

//Funktion for getting Map state to explore
function newState(kekeState, map) {
	simjs.clearLevel(kekeState);
	kekeState.orig_map = map;
	[kekeState.back_map, kekeState.obj_map] = simjs.splitMap(kekeState.orig_map);
	simjs.assignMapObjs(kekeState);
	simjs.interpretRules(kekeState);
  }
function giveaninitialsequence(parent){
	let s = [];
	if(parent==undefined){
		for(let i=0;i<15;i++){
			let action = possActions[Math.floor(Math.random()*possActions.length)];
			s.push(action);
		}
	}else{
		if(parent.actionHistory.length>50){
			
			for(let i=0;i<5;i++){//random Mutations
				//console.log("Mutatet",i)
				parent.actionHistory[Math.floor(Math.random()*parent.actionHistory.length)]=possActions[Math.floor(Math.random()*(possActions.length-1))+1];

			}
			for(let i=0;i<(parent.actionHistory.length);i++){//SpACEKILLER
				//console.log("space killed",i)
				if (parent.actionHistory[i]==="space"){parent.actionHistory[i]=possActions[Math.floor((Math.random()*(possActions.length-1))+1)];

				}
			}
			parent.actionHistory.length=50;//caps the path size (not hard)
		}
		for(let i=0;i<(Math.floor((parent.actionHistory.length)));i++){
			
			let action = parent.actionHistory[i];
			s.push(action);
			
			
		}
	}
	an_action_set = s;
	return s;
}
  //Function to figure out if next Path is a winning or dieing Path
  function Walk_through_and_check_the_new_Path_for_some_things(currState, parent) {
	// Append the child direction to the existing movement path.
   // let nextActions = [];
	//nextActions.push(...parent.actionHistory);
  //  nextActions=makeSeq();
  //  console.log("nextActions ", nextActions)
	let won = false;
	let died = false;
	Path = giveaninitialsequence(parent);

	tryfivetimes = 0;
	trymax=0;
	for (let a = 0; a < (Path.length); a += 1) {
	  
	  Path.push(possActions[Math.floor(Math.random()*possActions.length)]);

	  const statesaver = {};
	  newState(statesaver, currState.orig_map);
	  const nextMove = simjs.nextMove(Path[a], currState);
	  const nextState = nextMove.next_state;
	  won = nextMove.won;//Checks if the next move is a winning move
//	  console.log(won,"won");
	  if(won){
		const thisMap = simjs.doubleMap2Str(currState.obj_map, currState.back_map);
		const nextElementOnStack = new Node(thisMap, Path, parent, won, died);
		console.log("Winner Winner Chicken Dinner","Path",Path)
		return nextElementOnStack;
	  }
	  trymax++;
	  if(trymax==Math.floor((Path.length)/2)){
	//	  console.log("Looser Looser Mic Abuser","Path",Path)
		  const thisMap = simjs.doubleMap2Str(currState.obj_map, currState.back_map);
		  const nextElementOnStack = new Node(thisMap, Path, parent, won, died);
		  return nextElementOnStack;
	  }
	  if (nextState.players.length === 0) {//checks if Baba dies with the next move
	//	console.log(" Chicken Dinner",a)
		won = false;
		died = true;
		//console.log(a,"a/","\nDead",Path,"Path[a]",Path[a]")
		Path[a]=GivenextAction(Path[a]);
	//	console.log(Path[a],"Path[a]\n");
		tryfivetimes++;
		if(tryfivetimes>5){
			tryfivetimes=0;
			a++
		}//else{a++}
		a--;
		currState = statesaver;//makes baba try the actal move again diffrently
	  }
	}
	//Saves the map and creates a new node holding all the infos
	const thisMap = simjs.doubleMap2Str(currState.obj_map, currState.back_map);
	const nextElementOnStack = new Node(thisMap, Path, parent, won, died);
	return nextElementOnStack;
  }
  //funktion for makeing a random Path
  function makeSeq(){
	let s = [];
	for(let i=0;i<50;i++){
		let action = possActions[Math.floor(Math.random()*possActions.length)];
		s.push(action);
	}
	an_action_set = s;
	return s;
}
// NEXT ITERATION STEP FOR SOLVING
function iterSolve(init_state){
	const currState = {};
	//Initialise the mapState For the Next Try
    newState(currState, init_state.orig_map);

	const parent = stack.pop();
 //   console.log("parent",parent)
	const NextTry = Walk_through_and_check_the_new_Path_for_some_things(currState, parent);

	const alivePathStack = [];
	//If the Try has a map representation and Bab is not dead Push path to the Alive Stack
	if (!stateSet.has(NextTry.mapRep) && !NextTry.died) alivePathStack.push(NextTry);
  	
	stateSet.add(NextTry.mapRep);
	if (NextTry.won){ 
		console.log("WinningPath Node",NextTry)
		return NextTry.actionHistory
	}
	// PERFORM ITERATIVE CALCULATIONS HERE //

	
	//return a sequence of actions or empty list
	stack.push(NextTry)
	//Pushing Next Try to the stack so he gets new Latest Try
//	console.log("NextTry",NextTry)
	return NextTry.actionHistory;
}

function initState(init_state) {
	const stack = [];
	const firstElement = new Node(simjs.map2Str(init_state.orig_map), [], null, false, false);
	stack.push(firstElement);
//	console.log("firstElement",firstElement)
  }

// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
	step : function(init_state){return iterSolve(init_state)},		// iterative step function (returns solution as list of steps from poss_actions or empty list)
	init : function(init_state){  initState(init_state); },							// initializing function here
	best_sol : function(){return [];}				//returns closest solution in case of timeout
}
