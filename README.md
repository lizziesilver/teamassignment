# teamassignment

[`teamassignment.py`](https://github.com/lizziesilver/teamassignment/blob/master/teamassignment.py) is a Python script that assigns people to teams, based on their answers to the Individual Differences Survey. 

## Requirements:

* Python 3.6. Required Python packages are listed in [`requirements.txt`]().
* Java JRE 6 or later.
* The Java library [`mdgp_jors_2011.jar`](http://www.optsicom.es/mdgp/mdgp_jors_2011.jar) (also available [in this repo](https://github.com/lizziesilver/teamassignment/raw/master/mdgp_jors_2011.jar), in case [the Optsicom website](http://www.optsicom.es/mdgp/) goes down). This jar must be located in the same directory as the Python script, `teamassignment.py`. 
* Note: the Python script will write files to the same directory that are inputs and outputs for the Java library; their filenames are "`block_n_mdgp_solver_input.tx`" and "`block_n_mdgp_solver_output.txt`", where n is an integer, so make sure nothing in the folder is named that or it will be overwritten.
* Note: Input data must have variable names matching those in the [data dictionary](https://github.com/lizziesilver/teamassignment/raw/master/CREATE_Ind.Diffs_Data.Dictionary_Final_1.11.18.xlsx). 

## To run:

To test it, you can run it with [the sample data that T&E provided](https://3.basecamp.com/3591142/buckets/5168244/uploads/851270327). 

You can run the script from the command line like so:

```python teamassignment.py <inputfile.csv> <outputfile.csv> <num_teams_per_block> <condition>```

Input and output filenames are required. The last two arguments are optional; default values are **14** and **swarm**. The script will infer team size from the number of participants in the input data.

For the pilot, there should be 60 subjects in the SWARM condition, so `<num_teams_per_block>` should be 2. For the pilot, you would call the team assignment script like so:

```python teamassignment.py inputfile.csv outputfile.csv 2```

And if another performer (e.g. BARD) wants to use it, they can call it like so: 

```python teamassignment.py inputfile.csv outputfile.csv 2 bard```

I've hard-coded a time-limit for the solver, so it will take two minutes to assign each block of participants to teams.

## Background on the solver

My goal was to increase diversity within teams. This is an instance of the [Maximally Diverse Grouping Problem](http://www.optsicom.es/mdgp/) (MDGP). It's like an anti-clustering problem: you want to group elements together if they're different rather than similar.

Like clustering, the problem divides into two parts. First, define a distance function that tells you how different any two people are. Second, find a partition that maximises the sum of distances among the pairs within each group. The second step is what most MDGP papers address. 

Most recent MDGP papers benchmark their methods against a publicly available library of MDGP solvers, [available from the Optsicom website](http://www.optsicom.es/mdgp/#state-of-the-art-methods). I used this library. Unfortunately it's not open-source. You have to call the jar from the command line and pass it a text file of pairwise distances and constraints (number of teams, limits on team size). It then writes its solution to file.

## The wrapper
I wrote a Python wrapper that does the following:

1. Takes a CSV file of responses to the Individual Differences Survey
2. Calculates the distances between individuals & writes them to file
   * Features: for the psych tests, I only used the scores (I ignored responses to individual items, and the timing measures). I ignored college major and other language because they're free text input. Otherwise I used all the substantive variables.
   * Normalisation: I normalised each variable to have range 0-1
   * Distance function: Manhattan distance
6. Runs the MDGP solver on that input, interprets the solver's output, and writes the final team assignments to file.

It's pretty simple; if you want to modify, say, the distance function it should be straightforward. 

## Performance:

The MDGP solver dramatically improves covariate balance across teams, for all features, with real data. To evaluate performance, I took T&E's sample of 301 people, and used the solver to create 10 teams of 30 or 31 people. I looked at the variation among the team means on each variable. Compared to random assignments, the solver reduces the standard deviation of the mean by about 65% for all variables:

![Covariate balance improved 65% with the solver](img/balance.png?raw=true "Covariate balance improved 65% with the solver")

The solver also produces a small but consistent improvement in diversity within teams. The mean of the within-team standard deviations increased by about 3% for all variables:

![Team diversity improved 3% with the solver](img/diversity.png?raw=true "Team diversity improved 3% with the solver")

Note: In relative terms, the improvement in covariate balance looks larger than the improvement in within-team diversity. However, in absolute terms, the increase in within-team variance must be exactly the same size as the decrease in between-team variance. This follows from the [Law of Total Variance](https://en.wikipedia.org/wiki/Law_of_total_variance).
