# TheGivingScript
Script splits a number of tasks (ranked by suckiness) between a number of individuals. Keeping score for the sake of prosperity.

Usage
-----
TheGiver.py ['swap', {username}, 'losers']
* no params: kicks of a distribution of tasks
* 'swap':    trades a task from one user to another. Updates points as one would expect
* {user}:    shows record for the selected user
* 'losers':  shows how many rounds each user has lost.
 
How it Works
-----
During a round the script will order the users by score, and then assign randomly those tasks not yet assigned until all task have been handed out. If the number of users != number of tasks, this distribution method results in users with the highest score receiving fewer tasks (#users>#tasks: some users get no tasks, #users<#tasks: some users get 1 less task some of their peers).
