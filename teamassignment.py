# TO DO:
# Divide users by block, run team assignment on each block
# [done] Make sure team size bounds are feasible given sample size
# Range-normalize the distances for each variable 
# Detect & trim outlier distances for each variable
# Weight and sum distances for all variables
# For evaluation: try NOT excluding the other performer rows, and evaluate 
#     variance of results on all users
# See how different the results are over multiple runs
# [done] give four optional arguments:
#   number of teams per block
#   minimum team size
#   maximum team size
#   condition
# [done] check that arguments are feasible

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
    k = sys.argv[3]
    k_default = " (entered as command line argument)"
else:
    k = 14
    k_default = " (default)"

# default is min_n = 25 participants per team
if len(sys.argv) > 4:
    min_n = sys.argv[4]
    min_n_default = " (entered as command line argument)"
else:
    min_n = 25
    min_n_default = " (default)"

# default is max_n = 37 participants per team
if len(sys.argv) > 5:
    max_n = sys.argv[5]
    max_n_default = " (entered as command line argument)"
else:
    max_n = 37
    max_n_default = " (default)"

# default condition is SWARM, unless a value is provided as the 6th argument
if len(sys.argv) > 6:
    cond = sys.argv[6]
    cond_default = " (entered as command line argument)"
else:
    cond = "swarm"
    cond_default = " (default)"


# remove participants from other performers
df = input_data[input_data["cond"] == cond].copy()

# save the indices of the cells we'll need to change in the output data
cond_rows = np.where(input_data["cond"] == cond)[0]
team_col = np.where(input_data.columns.values == "team")[0]

# get list of unique blocks in this condition
blocks = df["block"].unique().tolist()

# n = list of sample sizes per block
n = df.groupby("block").size().tolist()

# if you divide participants into equal sized teams, they differ by at most 
# one participant. Natural upper and lower bounds:
lowers = [math.floor(b / float(k)) for b in n]
uppers = [math.ceil(b / float(k)) for b in n]

# TEST whether number of teams, sample size, and min+max team size constraints
# are all consistent. If inconsistent, exit with an error explaining which 
# blocks the constraint was violated for, whether default args were used, and 
# how to enter the optional arguments.

if not (all(l >= min_n for l in lowers) & all(u <= max_n for u in uppers)):
    msg = "The number of teams per block, sample size per block, and upper " + \
          "and lower limits on team size are incompatible with each other. " + \
          "Sample sizes per block in input file: " + str(n) + \
          ". Number of teams per block: " + str(k) + k_default + \
          ". Lower limit on team size: " + str(min_n) + min_n_default + \
          ". Upper limit on team size: " + str(max_n) + max_n_default + ". " + \
          "Enter these parameters via the command line as follows: \n\n" + \
          "teamassignment.py inputfile.csv outputfile.csv num_teams_per_block" + \
          " min_n_per_team max_n_per_team condition"
    sys.exit(msg)

# # test whether JDK is installed
# proc = subprocess.Popen("javac -version", stdout=subprocess.PIPE, shell=True)
# output = proc.stdout.read()
# have_java = output[0:5].decode("utf-8") == "javac"
# if not have_java:
#     msg = """You do not have the Java compiler installed. The Maximally 
#           Diverse Grouping Problem solver requires JDK 6 or higher. 
#           Please run `sudo apt-get install openjdk-8-jdk` and then try 
#           running this script again."""
#     sys.exit(msg)

relevant_vars = [#"block", 
#     "cond", 
#     "team", 
#     "requested_avatar", 
    "team_lead", 
    "age", 
    "gender", 
    "education", 
#     "college_major_1", 
#     "college_major_2", 
#     "college_minor_1", 
#     "college_minor_2", 
#     "occupation", 
    "english_proficiency", 
#     "other_lang_proficien_1", 
#     "other_lang_proficien_1_TEXT", 
#     "other_lang_proficien_2", 
#     "other_lang_proficien_2_TEXT", 
#     "other_lang_proficien_3", 
#     "other_lang_proficien_3_TEXT", 
#     "other_lang_proficien_4", 
#     "other_lang_proficien_4_TEXT", 
#     "other_lang_proficien_5", 
#     "other_lang_proficien_5_TEXT", 
#     "other_lang_proficien_6", 
#     "other_lang_proficien_6_TEXT", 
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
#     "prob_coher_35Acomp_1", 
#     "prob_coher_57A_1", 
#     "prob_coher_14Acomp_1", 
#     "prob_coher_60AUB_1", 
#     "prob_coher_5AUB_1", 
#     "matrix_1", 
#     "matrix_2", 
#     "matrix_3", 
#     "matrix_4", 
#     "matrix_5", 
#     "matrix_6", 
#     "matrix_7", 
#     "matrix_8", 
#     "matrix_9", 
#     "matrix_10", 
#     "matrix_11", 
    "score_matrix", # matrix reasoning test
#     "prob_reas_1", 
#     "prob_reas_2", 
#     "prob_reas_3", 
#     "prob_reas_4", 
#     "prob_reas_5", 
#     "prob_reas_6", 
#     "prob_reas_7", 
#     "prob_reas_8", 
#     "prob_reas_9", 
#     "prob_reas_10", 
#     "prob_reas_11", 
#     "prob_reas_12", 
#     "prob_reas_13", 
#     "prob_reas_14", 
#     "prob_reas_15", 
#     "prob_reas_16", 
    "score_prob_reas", # probabilistic reasoning test
#     "aomt_1", 
#     "aomt_2", 
#     "aomt_3", 
#     "aomt_4", 
#     "aomt_4_rev", 
#     "aomt_5", 
#     "aomt_5_rev", 
#     "aomt_6", 
#     "aomt_6_rev", 
#     "aomt_7", 
#     "aomt_7_rev", 
#     "aomt_8", 
#     "aomt_9", 
#     "aomt_9_rev", 
#     "aomt_10", 
#     "aomt_11", 
    "score_aomt", # actively open-minded thinking test
#     "bfi_1", 
#     "bfi_2", 
#     "bfi_3", 
#     "bfi_4", 
#     "bfi_5", 
#     "bfi_6", 
#     "bfi_7", 
#     "bfi_8", 
#     "bfi_9", 
#     "bfi_10", 
#     "bfi_1_rev", 
#     "bfi_3_rev", 
#     "bfi_4_rev", 
#     "bfi_5_rev", 
#     "bfi_7_rev", 
    "score_bfi_openness", # big five personality inventory
    "score_bfi_conscientiousness", 
    "score_bfi_extraversion", 
    "score_bfi_agreeableness", 
    "score_bfi_neuroticism", 
#     "toa_1", 
#     "toa_2", 
#     "toa_2_rev", 
#     "toa_3", 
#     "toa_4", 
#     "toa_4_rev", 
#     "toa_5", 
#     "toa_6", 
#     "toa_6_rev", 
#     "toa_7", 
#     "toa_8", 
#     "toa_8_rev", 
#     "toa_9", 
#     "toa_10", 
#     "toa_10_rev", 
#     "toa_11", 
#     "toa_12", 
#     "toa_12_rev", 
#     "toa_13", 
#     "toa_14", 
#     "toa_14_rev", 
#     "toa_15", 
#     "toa_16", 
#     "toa_16_rev", 
    "score_toa_novelty", # tolerance of ambiguity
    "score_toa_complexity", 
    "score_toa_insolubility", 
#     "rme_1", 
#     "rme_2", 
#     "rme_3", 
#     "rme_4", 
#     "rme_5", 
#     "rme_6", 
#     "rme_7", 
#     "rme_8", 
#     "rme_9", 
#     "rme_10", 
#     "rme_11", 
#     "rme_12", 
#     "rme_13", 
#     "rme_14", 
#     "rme_15", 
#     "rme_16", 
#     "rme_17", 
#     "rme_18", 
#     "rme_19", 
#     "rme_20", 
#     "rme_21", 
#     "rme_22", 
#     "rme_23", 
#     "rme_24", 
#     "rme_25", 
#     "rme_26", 
#     "rme_27", 
#     "rme_28", 
#     "rme_29", 
#     "rme_30", 
#     "rme_31", 
#     "rme_32", 
#     "rme_33", 
#     "rme_34", 
#     "rme_35", 
#     "rme_36", 
    "score_rme", # Mind in the Eyes
#     "prob_coher_14A_1", 
#     "prob_coher_35A_1", 
#     "prob_coher_5A_1", 
#     "prob_coher_60A_1", 
#     "prob_coher_5Acomp_1", 
#     "prob_coher_57Acomp_1", 
#     "prob_coher_60Acomp_1", 
#     "prob_coher_14B_1", 
#     "prob_coher_35B_1", 
#     "prob_coher_5B_1", 
#     "prob_coher_57B_1", 
#     "prob_coher_60B_1", 
#     "prob_coher_14AUB_1", 
#     "prob_coher_35AUB_1", 
#     "prob_coher_57AUB_1", 
    "coh_score_4way", 
    "coh_score_3way", 
    "coh_score_2way"]

# convert gender and age into numeric variables
df.loc[:,"gender"] = [int(x == "f") for x in df.loc[:,"gender"]]
age_dict = {'18-24':0, '25-34':1, '35-44':2, '45-54':3, '55-64':4, '65+':5}
df.loc[:,["age"]] = [age_dict[x] for x in df.loc[:,"age"]]

# subset to relevant variables
df = df[relevant_vars]

# replace null values with medians
for i in range(df.shape[1]):
    good_enough = df.iloc[:,i].median()
    df.iloc[np.where(df.isnull().iloc[:, i])[0], i] = good_enough

# team size limits
# TODO: include a test of whether the sample size is too small or too large
lims = " " + str(min_n) + " " + str(max_n)

# where to write the file for the solver
instance_filename = 'mdgp_solver_input.txt'

# if instance file already exists, remove it
try:
    os.remove(instance_filename)
except OSError:
    pass

# TODO: incorporate new distance function here
# write distances to file
with open(instance_filename, 'a') as the_file:
    the_file.write(str(n) + " " + str(k) + " ss" + str(lims)*k + "\n")
    for i in range(n):
        for j in range(i+1, n):
            mdist = scipy.spatial.distance.cityblock(df.iloc[i], df.iloc[j])
            the_file.write(str(i) + " " + str(j) + " " + str(mdist) + "\n")

# run solver on instance file, write data to solver file
import subprocess
solver_filename = "mdgp_solver_output.txt"
bash_command = "java -jar mdgp_jors_2011.jar SO " + instance_filename + " 60000 > " + solver_filename
subprocess.call(bash_command, shell=True)

# read solution from file 
with open(solver_filename) as f:
    content = f.readlines()

# remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

# identify line where solution is written
sol_index = np.where([item.startswith('Solution: [') for item in content])

# turn into list of ints
solution = [int(x) for x in content[sol_index[0][0]][11:-1].split(", ")]

# add MDGP solution to dataframe of initial data
input_data.iloc[cond_rows, team_col] = solution

# write to file
input_data.to_csv(outputfile)
