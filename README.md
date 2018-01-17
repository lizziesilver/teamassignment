# teamassignment

[`teamassignment.py`](https://github.com/lizziesilver/teamassignment/blob/master/teamassignment.py) is a Python script that assigns people to teams, based on their answers to the Individual Differences Survey. 

## Requirements:

* It requires the Java library [`mdgp_jors_2011.jar`](http://www.optsicom.es/mdgp/mdgp_jors_2011.jar) (also available [in this repo](https://github.com/lizziesilver/teamassignment/raw/master/mdgp_jors_2011.jar), in case [the Optsicom website](http://www.optsicom.es/mdgp/) goes down).
* The Java library, `mdgp_jors_2011.jar`, must be in the same directory as the script, `teamassignment.py`. 
* The python script will write files to the same directory that are inputs and outputs for this Java library; their filenames are "`block_n_mdgp_solver_input.tx`" and "`block_n_mdgp_solver_output.txt`", where n is an integer, so make sure nothing in the folder is named that or it will be overwritten. 

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

## Performance:

The MDGP solver dramatically improves covariate balance across teams, for all features, with real data. To evaluate performance, I took T&E's sample of 301 people, and used the solver to create 10 teams of 30 or 31 people. I looked at the variation among the team means on each variable. Compared to random assignment, the solver reduces the standard deviation of the mean by about 65% for all variables:

![Covariate balance improved 65% with the solver](img/balance.png?raw=true "Covariate balance improved 65% with the solver")

The solver also produces a small but consistent improvement in diversity within teams. The mean of the within-team standard deviations increased by about 3% for all variables:

![Team diversity improved 3% with the solver](img/diversity.png?raw=true "Team diversity improved 3% with the solver")
