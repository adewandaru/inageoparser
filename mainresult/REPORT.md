# EVENT


## CRF, Baseline
entity options: gaz|postag
['B-ARG', 'I-ARG', 'B-EVE', 'I-EVE', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG']
start testing/evaluation
              precision    recall  f1-score   support

       B-ARG      0.856     0.697     0.768       231
       I-ARG      0.812     0.728     0.768       250
       B-EVE      0.917     0.741     0.820       135
       I-EVE      0.857     0.750     0.800        24
       B-LOC      0.881     0.875     0.878       160
       I-LOC      0.943     0.892     0.917        74
       B-ORG      0.919     0.680     0.782        50
       I-ORG      0.772     0.721     0.746        61

   micro avg      0.861     0.756     0.805       985
   macro avg      0.870     0.760     0.810       985
weighted avg      0.862     0.756     0.804       985

## NCRFPP, Baseline
              precision    recall  f1-score   support

       B-ARG      0.860     0.693     0.767       231
       I-ARG      0.908     0.668     0.770       250
       B-EVE      0.881     0.874     0.877       135
       I-EVE      0.800     0.833     0.816        24
       B-LOC      0.884     0.950     0.916       160
       I-LOC      0.904     0.892     0.898        74
       B-ORG      0.884     0.760     0.817        50
       I-ORG      0.872     0.672     0.759        61

   micro avg      0.882     0.774     0.824       985
   macro avg      0.874     0.793     0.828       985
weighted avg      0.883     0.774     0.820       985


## CRF. Proposed
entity options: org_regex|arg_regex|ev_keywords|gaz|postag
['B-ARG', 'I-ARG', 'B-EVE', 'I-EVE', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG']
start testing/evaluation
              precision    recall  f1-score   support

       B-ARG      0.861     0.723     0.786       231
       I-ARG      0.855     0.752     0.800       250
       B-EVE      0.920     0.770     0.839       135
       I-EVE      0.769     0.833     0.800        24
       B-LOC      0.866     0.887     0.877       160
       I-LOC      0.943     0.892     0.917        74
       B-ORG      0.722     0.780     0.750        50
       I-ORG      0.712     0.770     0.740        61

   micro avg      0.852     0.785     0.817       985
   macro avg      0.831     0.801     0.813       985
weighted avg      0.856     0.785     0.817       985


## NCRF, Proposed


raw: time:0.79s, speed:235.20st/s; acc: 0.9131, p: 0.7968, r: 0.7691, f: 0.7827
Predict raw 10-best result has been written into file. sample_data/entity_raw.out
              precision    recall  f1-score   support

       B-ARG      0.803     0.740     0.770       231
       I-ARG      0.807     0.804     0.806       250
       B-EVE      0.892     0.859     0.875       135
       I-EVE      0.769     0.833     0.800        24
       B-LOC      0.909     0.938     0.923       160
       I-LOC      0.895     0.919     0.907        74
       B-ORG      0.833     0.800     0.816        50
       I-ORG      0.880     0.721     0.793        61

   micro avg      0.846     0.822     0.834       985
   macro avg      0.849     0.827     0.836       985
weighted avg      0.846     0.822     0.833       985


# EVENT

                  precision    recall  f1-score   support

B-ACCIDENT-EVENT      1.000     0.710     0.830        31
I-ACCIDENT-EVENT      1.000     1.000     1.000         4
    B-FIRE-EVENT      0.962     0.676     0.794        37
    I-FIRE-EVENT      1.000     0.714     0.833         7
   B-FLOOD-EVENT      0.857     0.750     0.800        24
   I-FLOOD-EVENT      0.857     0.750     0.800         8
   B-QUAKE-EVENT      0.929     0.839     0.881        31
   I-QUAKE-EVENT      0.750     0.750     0.750         4

       micro avg      0.932     0.747     0.829       146
       macro avg      0.919     0.774     0.836       146
    weighted avg      0.937     0.747     0.828       146

## NCRF, BASELINE FEATURE


raw: time:0.72s, speed:257.44st/s; acc: 0.9861, p: 0.8548, r: 0.7910, f: 0.8217
Predict raw 10-best result has been written into file. sample_data/event_raw.out
                  precision    recall  f1-score   support

B-ACCIDENT-EVENT      1.000     0.903     0.949        31
I-ACCIDENT-EVENT      0.667     1.000     0.800         4
    B-FIRE-EVENT      0.917     0.892     0.904        37
    I-FIRE-EVENT      1.000     0.857     0.923         7
   B-FLOOD-EVENT      0.808     0.875     0.840        24
   I-FLOOD-EVENT      0.750     0.750     0.750         8
   B-QUAKE-EVENT      0.906     0.935     0.921        31
   I-QUAKE-EVENT      0.667     1.000     0.800         4

       micro avg      0.885     0.897     0.891       146
       macro avg      0.839     0.902     0.861       146
    weighted avg      0.895     0.897     0.893       146

## NCRF, PROPOSED FEATURE

raw: time:0.80s, speed:231.67st/s; acc: 0.9981, p: 0.9699, r: 0.9627, f: 0.9663
Predict raw 10-best result has been written into file. sample_data/event_raw.out
                  precision    recall  f1-score   support

B-ACCIDENT-EVENT      1.000     0.935     0.967        31
I-ACCIDENT-EVENT      1.000     1.000     1.000         4
    B-FIRE-EVENT      0.974     1.000     0.987        37
    I-FIRE-EVENT      1.000     1.000     1.000         7
   B-FLOOD-EVENT      1.000     1.000     1.000        24
   I-FLOOD-EVENT      1.000     1.000     1.000         8
   B-QUAKE-EVENT      1.000     0.968     0.984        31
   I-QUAKE-EVENT      1.000     1.000     1.000         4

       micro avg      0.993     0.979     0.986       146
       macro avg      0.997     0.988     0.992       146
    weighted avg      0.993     0.979     0.986       146

# ARG

## NCRFPP, BASELINE FEATURE
    raw: time:2.08s, speed:89.23st/s; acc: 0.9073, p: 0.7163, r: 0.6871, f: 0.7014
Predict raw 10-best result has been written into file. sample_data/arg_raw.out
                       precision    recall  f1-score   support

    B-DeathVictim-Arg      0.750     0.522     0.615        23
         B-Height-Arg      0.688     0.611     0.647        18
B-OfficerOfficial-Arg      0.786     0.759     0.772        29
          B-Place-Arg      0.816     0.884     0.849       146
         B-Street-Arg      0.833     0.750     0.789        20
       B-Strength-Arg      0.857     0.462     0.600        13
           B-Time-Arg      0.984     0.984     0.984        61
        B-Vehicle-Arg      0.625     0.625     0.625        16

            micro avg      0.828     0.813     0.820       326
            macro avg      0.792     0.699     0.735       326
         weighted avg      0.826     0.813     0.815       326

## NCRFPP, PROPOSED FEATURE
raw: time:1.92s, speed:96.46st/s; acc: 0.9577, p: 0.8636, r: 0.8617, f: 0.8627
Predict raw 10-best result has been written into file. sample_data/arg_raw.out
                       precision    recall  f1-score   support

    B-DeathVictim-Arg      0.808     0.913     0.857        23
         B-Height-Arg      0.889     0.889     0.889        18
B-OfficerOfficial-Arg      0.897     0.897     0.897        29
          B-Place-Arg      0.932     0.945     0.939       146
         B-Street-Arg      0.941     0.800     0.865        20
       B-Strength-Arg      1.000     0.769     0.870        13
           B-Time-Arg      0.984     0.984     0.984        61
        B-Vehicle-Arg      0.938     0.938     0.938        16

            micro avg      0.929     0.926     0.928       326
            macro avg      0.923     0.892     0.905       326
         weighted avg      0.931     0.926     0.928       326

## CRF. BASELINE
arg options: gaz|postag
['B-DeathVictim-Arg', 'B-Vehicle-Arg', 'B-Height-Arg', 'B-OfficerOfficial-Arg', 'B-Place-Arg', 'B-Time-Arg', 'B-Street-Arg', 'B-Strength-Arg']
start testing/evaluation
                       precision    recall  f1-score   support

    B-DeathVictim-Arg      0.867     0.565     0.684        23
         B-Height-Arg      0.818     0.500     0.621        18
B-OfficerOfficial-Arg      0.824     0.483     0.609        29
          B-Place-Arg      0.809     0.781     0.794       146
         B-Street-Arg      0.846     0.550     0.667        20
       B-Strength-Arg      1.000     0.308     0.471        13
           B-Time-Arg      0.967     0.951     0.959        61
        B-Vehicle-Arg      0.583     0.438     0.500        16

            micro avg      0.842     0.706     0.768       326
            macro avg      0.839     0.572     0.663       326
         weighted avg      0.843     0.706     0.756       326

## CRF. Proposed
arg options: ev_keywords|entity
merge the X_test's word.entity feature using y_test from previous train session
['B-DeathVictim-Arg', 'B-Vehicle-Arg', 'B-Height-Arg', 'B-OfficerOfficial-Arg', 'B-Place-Arg', 'B-Time-Arg', 'B-Street-Arg', 'B-Strength-Arg']
start testing/evaluation
                       precision    recall  f1-score   support

    B-DeathVictim-Arg      0.815     0.957     0.880        23
         B-Height-Arg      1.000     0.778     0.875        18
B-OfficerOfficial-Arg      0.707     1.000     0.829        29
          B-Place-Arg      0.938     0.938     0.938       146
         B-Street-Arg      0.895     0.850     0.872        20
       B-Strength-Arg      1.000     0.615     0.762        13
           B-Time-Arg      0.923     0.984     0.952        61
        B-Vehicle-Arg      0.600     0.938     0.732        16

            micro avg      0.875     0.926     0.900       326
            macro avg      0.860     0.882     0.855       326
         weighted avg      0.893     0.926     0.902       326
# PLOC

raw: time:0.63s, speed:295.38st/s; acc: 0.9693, p: 0.6188, r: 0.7000, f: 0.6569
Predict raw 5-best result has been written into file. sample_data/ploc_raw.out
              precision    recall  f1-score   support

       B-LOC      0.570     0.878     0.691        74
       I-LOC      0.629     0.647     0.638        34
      B-PLOC      0.866     0.674     0.758        86
      I-PLOC      0.818     0.675     0.740        40

   micro avg      0.691     0.735     0.712       234
   macro avg      0.721     0.719     0.707       234
weighted avg      0.730     0.735     0.716       234

## CRF. Baseline

ploc options: gaz|postag
['B-LOC', 'B-PLOC', 'I-LOC', 'I-PLOC']
start testing/evaluation
              precision    recall  f1-score   support

       B-LOC      0.633     0.419     0.504        74
       I-LOC      0.731     0.559     0.633        34
      B-PLOC      0.762     0.709     0.735        86
      I-PLOC      0.711     0.675     0.692        40

   micro avg      0.715     0.590     0.646       234
   macro avg      0.709     0.591     0.641       234
weighted avg      0.708     0.590     0.640       234

## CRF. Proposed
ploc options: ismax|arg
merge the X_test's word.arg feature using y_pred from previous train arg and event session
['B-LOC', 'B-PLOC', 'I-LOC', 'I-PLOC']
start testing/evaluation
              precision    recall  f1-score   support

       B-LOC      0.825     0.635     0.718        74
       I-LOC      0.710     0.647     0.677        34
      B-PLOC      0.745     0.884     0.809        86
      I-PLOC      0.705     0.775     0.738        40

   micro avg      0.752     0.752     0.752       234
   macro avg      0.746     0.735     0.735       234
weighted avg      0.758     0.752     0.749       234


## NCRFPP. Proposed 
ismax|arg|event

Predict raw 5-best result has been written into file. sample_data/ploc_raw.out
              precision    recall  f1-score   support

       B-LOC      0.786     0.743     0.764        74
       I-LOC      0.784     0.853     0.817        34
      B-PLOC      0.798     0.826     0.811        86
      I-PLOC      0.842     0.800     0.821        40

   micro avg      0.799     0.799     0.799       234
   macro avg      0.802     0.805     0.803       234
weighted avg      0.799     0.799     0.799       234

