# TO DO:
# Detect & trim outlier distances for each variable
# Weight distances for all variables
# For evaluation: try NOT excluding the other performer rows, and evaluate 
#     variance of results on all users
# See how different the results are over multiple runs

# requirements 
import pandas as pd
import numpy as np
import random
import scipy.spatial
import os
import subprocess
import sys
import math

# get input and output filenames from sys argv
inputfile = sys.argv[1]
outputfile = sys.argv[2]
input_data = pd.DataFrame.from_csv(inputfile)

# default is k = 14 teams per block (following the Dec 8 version of the 
# experimental design) unless a value is provided as the third argument
if len(sys.argv) > 3:
    k = int(sys.argv[3])
    k_default = False
    print("User entered number of teams per block: " + str(k))
else:
    k = 14
    k_default = True
    print("Using default number of teams per block: 14")

# default condition is SWARM, unless a value is provided as the 4th argument
if len(sys.argv) > 4:
    cond = sys.argv[4]
    cond_default = False
    print("User entered condition: " + cond)
else:
    cond = "swarm"
    cond_default = True
    print("Using default condition: swarm")

print("Arranging input data")

# remove participants from other performers
df = input_data[input_data["cond"] == cond].copy()

# get list of unique blocks in this condition
blocks = df["block"].unique().tolist()

# save the indices of the cells we'll need to change in the output data
team_col = np.where(input_data.columns.values == "team")[0]
block_rows = {}
for b in blocks:
    block_rows[b] = np.where((input_data["cond"] == cond) & \
                             (input_data["block"] == b))[0]

# block_n = dict of sample sizes per block
block_n = df.groupby("block").size().to_dict()

# if you divide participants into equal sized teams, they differ by at most 
# one participant. Natural upper and lower bounds on team size:
lowers = {x: math.floor(block_n[x] / float(k)) for x in list(block_n.keys())}
uppers = {x: math.ceil(block_n[x] / float(k)) for x in list(block_n.keys())}

# variables that contribute to the distance function
relevant_vars = ["block", 
    "team_lead", 
    "age", 
    "gender", 
    "education", 
    "english_proficiency", 
    "enjoy_logic_probs", 
    "enjoy_num_probs", 
    "expertise_math", 
    "expertise_quant_model", 
    "expertise_stats", 
    "expertise_prob", 
    "expertise_bayes_net", 
    "expertise_programming", 
    "expertise_exp_design", 
    "expertise_risk_analysis", 
    "expertise_forecasting", 
    "expertise_dec_theory", 
    "expertise_game_theory", 
    "expertise_sats", 
    "expertise_arg_map", 
    "expertise_inf_logic", 
    "expertise_sys_think", 
    "expertise_image_analysis", 
    "expertise_link_analysis", 
    "expertise_graphic_design", 
    "expertise_tech_writing", 
    "score_matrix", # matrix reasoning test
    "score_prob_reas", # probabilistic reasoning test
    "crt_seen_before", 
    "score_crt", 
    "score_aomt", # actively open-minded thinking test
    "score_bfi_openness", # big five personality inventory
    "score_bfi_conscientiousness", 
    "score_bfi_extraversion", 
    "score_bfi_agreeableness", 
    "score_bfi_neuroticism", 
    "score_toa_novelty", # tolerance of ambiguity
    "score_toa_complexity", 
    "score_toa_insolubility", 
    "score_rme", # Mind in the Eyes
    "coh_score_4way", 
    "coh_score_3way", 
    "coh_score_2way"]

# subset to relevant variables
df = df[relevant_vars]

# convert gender and age into numeric variables
df.loc[:,"gender"] = [int(x == "f") for x in df.loc[:,"gender"]]
age_dict = {'18-24':0, '25-34':1, '35-44':2, '45-54':3, '55-64':4, '65+':5}
df.loc[:,["age"]] = [age_dict[x] for x in df.loc[:,"age"]]

# fix up data in each column (except block)
for i in range(df.shape[1]):
    if df.columns[i] != 'block':
        # replace null values with column medians
        df.iloc[np.where(df.isnull().iloc[:, i])[0], i] = df.iloc[:,i].median()
        # and normalize the range of every column 
        df.iloc[:,i] = df.iloc[:,i] - df.iloc[:,i].min() 
        df.iloc[:,i] = df.iloc[:,i] / df.iloc[:,i].max()

# make copy of df with all blocks before subsetting by block
fulldf = df.copy()

# run solver once for each block
for b in blocks:
    print("Writing input file for MDGP solver for Block " + str(b))
    
    # subset by block, then drop the "block" column
    df = fulldf[fulldf["block"] == b].copy()
    df.drop("block", axis=1, inplace=True)
    
    # where to write the file for the solver
    instance_filename = 'block_' + str(b) + '_mdgp_solver_input.txt'

    # if instance file already exists, remove it
    try:
        os.remove(instance_filename)
    except OSError:
        pass
    
    # create instance file for MDGP solver
    with open(instance_filename, 'a') as the_file:
        # first line has sample size, number of teams, "same size", and 
        # size limits for each team
        lims = " " + str(lowers[b]) + " " + str(uppers[b]) 
        the_file.write(str(block_n[b]) + " " + str(k) + " ss" + \
                       str(lims) * k + "\n")
        # following lines have row numbers identifying a pair of participants, 
        # and the distance between that pair.
        for i in range(block_n[b]):
            for j in range(i+1, block_n[b]):
                mdist = scipy.spatial.distance.cityblock(df.iloc[i], df.iloc[j])
                the_file.write(str(i) + " " + str(j) + " " + str(mdist) + "\n")
    
    print("Running MDGP solver for Block " + str(b) + ", this step takes 2 min")
        
    # run solver on instance file, write data to solver file
    solver_filename = "block_" + str(b) + "_mdgp_solver_output.txt"
    bash_command = "java -jar mdgp_jors_2011.jar SO " + instance_filename + \
                     " 120000 > " + solver_filename
    subprocess.call(bash_command, shell=True)
    
    print("Reading solution for Block " + str(b))
    
    # read solution from file 
    with open(solver_filename) as f:
        content = f.readlines()

    # remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]

    # identify line where solution is written
    sol_index = np.where([item.startswith('Solution: [') for item in content])

    # turn into list of ints
    solution = [int(x) for x in content[sol_index[0][0]][11:-1].split(", ")]
    
    # check solution is right length
    if len(solution) != df.shape[0]:
        sys.exit("Something's wrong. Check the solver file: " + solver_filename)
    
    # turn ints into strings with form "team<n>", with n starting from 1
    team_names = ['team' + str(s + 1 + (b - 1) * k) for s in solution]
    
    # add MDGP solution to dataframe of initial data
    input_data.iloc[block_rows[b], team_col] = team_names

print("Finished all blocks, writing team assignment to output file")
    
# write to file
input_data.to_csv(outputfile)


