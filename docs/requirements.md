# Requirements

## Functional Requirements

### FR1: New Initial Storyline Creation  
The system must allow users to create a new initial storyline by selecting a genre.

#### Preconditions  
- The user is authenticated.  

#### Postconditions  
- The user is redirected to the story interface.  

#### Main Event Flow  
1. The user selects "Create New Story" from the home page.  
2. The system prompts the user to choose a genre (e.g., fantasy, sci-fi, mystery, horror, etc.).  
3. The system generates the initial storyline.  
4. The system displays the initial storyline in the story interface.

### FR2: Subsequent Storylines Creation  
The system must allow users to create a new storyline by prompting for a decision when the previous storyline has ended.

#### Preconditions  
- The user is engaged in an interactive story session.  
- The previous storyline has reached a decision point.  

#### Postconditions  
- A new storyline is generated based on the user's decision.  
- The story progresses dynamically according to the new storyline.  

#### Main Event Flow  
1. The system detects that the current storyline has ended.  
2. The system prompts the user to make a decision in natural language.  
3. The user provides a decision input.  
4. The system generates a new storyline based on the user's decision.  
5. The system displays the new storyline and updates the story interface.

### FR3: Branch Creation in the Story Tree Interface  
The system must allow users to create new story branches by selecting decision points in the story tree interface and making new decisions.  

#### Preconditions  
- The user is engaged in an interactive story session.  
- The user has access to the story tree interface through the story interface.  

#### Postconditions  
- A new branch is created at the selected decision point.  
- The story tree is updated to reflect the new branch.  
- The user is redirected to the newly created branch.  

#### Main Event Flow  
1. The user accesses the story tree interface from the story interface.  
2. The system displays a visual representation of the story structure, showing all decision points.  
3. The user selects a decision point where they want to create a new branch.  
4. The system prompts the user to make a new decision.  
5. The user provides a decision input.  
6. The system generates a new storyline based on the new decision.  
7. The system updates the story tree with the newly created branch.  
8. The user is redirected to the new branch and can continue interacting with the story.

### FR4: Story Tree Navigation and Playback  
The system must allow users to navigate the story tree, select individual branches, replay them, and at the end of a branch, either take the last decision again or make a new decision to create a new branch.  

#### Preconditions  
- The user is engaged in an interactive story session.  
- The user has access to the story tree interface through the story interface.  

#### Postconditions  
- The selected branch is displayed.  
- The user can rewatch or review the storyline of the selected branch.  
- The user has the option to take the last decision again or make a new decision, creating a new branch.  
- The story tree is updated if a new branch is created.  

#### Main Event Flow  
1. The user accesses the story tree interface from the story interface.  
2. The system displays a visual representation of the story structure, showing all branches and decision points.  
3. The user selects a branch to review.  
4. The system loads and displays the selected branch's storyline.  
5. The user can rewatch or review the content of that branch.  
6. At the end of the branch, the system presents two options:  
   - Take the last decision again: The system regenerates the storyline based on the last choice.  
   - Make a new decision: The user provides a new decision input, creating a new branch.  
7. If the user chooses to make a new decision:  
   - The system generates a new storyline based on the new decision.  
   - The system updates the story tree with the newly created branch.  
   - The user is redirected to the new branch.  
8. The user can return to the story tree interface or continue interacting with the story.

### FR5: Progress Bar Navigation in the Story Player  
The system must allow users to navigate through the last watched path of the story tree using the progress bar in the story player. The progress bar will only display progress up to the next decision point that has not yet been made.

#### Preconditions  
- The user is engaged in an interactive story session.  
- The user has previously watched at least one branch of the story.  
- The progress bar represents the timeline of the last watched path in the story tree.  

#### Postconditions  
- The system updates the story playback to the selected position.  
- The user continues watching the story from the selected point.  
- The system maintains the consistency of the last watched path when navigating.  

#### Main Event Flow  
1. The user interacts with the progress bar in the story player.  
2. The system identifies the corresponding position in the last watched path of the story tree.  
3. The system updates playback to the selected position.  
4. If the user reaches a decision point, the system prompts the user to make a choice.  
5. The user can either:  
   - Take the last decision again: The system regenerates the storyline based on the last choice.  
   - Make a new decision: The user provides a new decision input, creating a new branch. 
6. If the user makes a decision, the system updates the story tree and progress bar to reflect the new branch.  
7. The user continues watching the story, with the progress bar dynamically updating based on the new path.  

### FR6: Playback Controls in the Story Player  
The system must allow users to control playback by pausing and adjusting the volume in the story player.  

#### Preconditions  
- The user is engaged in an interactive story session.  
- The story player is active.  

#### Postconditions  
- The playback is paused or resumed based on the user’s action.  
- The volume is adjusted based on the user’s preference.  

#### Main Event Flow  
1. The user interacts with the story player controls.  
2. The system provides the following options:  
   - Pause/Play: The user can pause or resume playback.  
   - Volume Control: The user can increase, decrease, or mute the volume.  
3. The system applies the selected action in real time.  
4. The user continues interacting with the story as needed.  

### FR7: Story Continuation from Homepage  
The system must allow users to revisit previously created stories from the homepage and continue from the last stopped point.  

#### Preconditions  
- The user is authenticated.  
- The user has at least one previously created story.  

#### Postconditions  
- The selected story is loaded in the story interface.  
- The story continues from the last stopped point.  

#### Main Event Flow  
1. The user accesses the homepage.  
2. The system displays a list of previously created stories.  
3. The user selects a story to continue.  
4. The system retrieves the last stopped point in the selected story.  
5. The system loads the story interface at the last stopped point.  
6. The user resumes interacting with the story.  
