
SEED: 42

# ABLATION RESULT:

Out[908]: 
{'ncrf:': True,
 'entity:': {'': 0.8157015382232108,
  'gaz': 0.8212250050395495,
  'gaz+postag': 0.8076190358937003,
  'org_regex+gaz+postag': 0.8249629084956561,
  'org_regex+arg_regex+gaz+postag': 0.8203818317381278,
  'org_regex+arg_regex+ev_keywords+gaz+postag': 0.834906046850458,
  'ev_keywords': 0.825804504123227,
  'ev_keywords+gaz+postag': 0.8262263688274037},
 'event:': {'': 0.8989888764404609,
  'gaz': 0.8852045454545454,
  'gaz+postag': 0.8776423486666073,
  'org_regex+gaz+postag': 0.8905071379428964,
  'org_regex+arg_regex+gaz+postag': 0.8973488410996077,
  'org_regex+arg_regex+ev_keywords+gaz+postag': 0.9091916676632347,
  'ev_keywords': 0.8991545138610564,
  'ev_keywords+gaz+postag': 0.8840907577201573,
  'ev_keywords+gaz+postag+entity': 0.9919354838709677,
  'arg_regex+ev_keywords+gaz+postag+entity': 0.9797619047619047,
  'ev_keywords+entity': 0.9919871794871794,
  'org_regex+arg_regex+ev_keywords+gaz+postag+entity': 0.9839039548022599},
 'arg:': {'': 0.7685953993444197,
  'gaz': 0.7885864382198783,
  'gaz+postag': 0.7588884503257921,
  'org_regex+gaz+postag': 0.800001068043815,
  'org_regex+arg_regex+gaz+postag': 0.806470514053498,
  'org_regex+arg_regex+ev_keywords+gaz+postag': 0.7804355851006676,
  'ev_keywords': 0.7848391959196023,
  'ev_keywords+gaz+postag': 0.7848837090402772,
  'ev_keywords+gaz+postag+entity': 0.8914008663384525,
  'arg_regex+ev_keywords+gaz+postag+entity': 0.9019611282240231,
  'ev_keywords+entity': 0.8939372353964647,
  'entity+event': 0.9064869745834438,
  'org_regex+arg_regex+ev_keywords+gaz+postag+entity': 0.8999962310326229,
  'org_regex+arg_regex+ev_keywords+gaz+postag+entity+event': 0.8981233475535926,
  'ev_keywords+gaz+entity+event': 0.8955197704263917},
 'ploc:': {'': 0.6703370036703371,
  'gaz': 0.773065373065373,
  'gaz+postag': 0.7228123903403834,
  'org_regex+gaz+postag': 0.75,
  'org_regex+arg_regex+gaz+postag': 0.8559216296680626,
  'org_regex+arg_regex+ev_keywords+gaz+postag': 0.8625730994152047,
  'ev_keywords': 0.6656714561174348,
  'ev_keywords+gaz+postag': 0.6911784511784512,
  'ev_keywords+gaz+postag+entity': 0.8304223766202192,
  'arg_regex+ev_keywords+gaz+postag+entity': 0.8796941990805311,
  'ev_keywords+entity': 0.8275862068965517,
  'entity+event': 0.8074116743471583,
  'org_regex+arg_regex+ev_keywords+gaz+postag+entity': 0.8603521554341226,
  'org_regex+arg_regex+ev_keywords+gaz+postag+entity+event': 0.866905273204486,
  'ev_keywords+gaz+entity+event': 0.8133944486885664,
  'ev_keywords+gaz+entity+event+arg': 0.7732703377864667,
  'ev_keywords+gaz+entity+event+arg+ismax': 0.7898868049243989,
  'arg_regex+ev_keywords+gaz+entity+event+arg+ismax': 0.8631343207614395,
  'org_regex+arg_regex+ev_keywords+gaz+entity+event+arg+ismax': 0.8692755825734549,
  'ismax': 0.7674074074074074,
  'ismax+arg': 0.8882991793208512,
  'ismax+arg+event': 0.8980414746543779,
  'ismax+arg+entity+event': 0.7760421040844322}}

# Final Result (Tables)
## ENTITY 
### Baseline

entity options: gaz+postag
              precision    recall  f1-score   support

         LOC      0.929     0.897     0.912       174
         ARG      0.762     0.767     0.764       347
         ORG      0.697     0.847     0.765       144
         EVE      0.850     0.888     0.869       134
   micro avg      0.797     0.830     0.813       799
   macro avg      0.809     0.850     0.828       799
weighted avg      0.801     0.830     0.814       799

### Proposed

entity options: org_regex+arg_regex+ev_keywords+gaz+postag
              precision    recall  f1-score   support

         LOC      0.951     0.897     0.923       174
         ARG      0.857     0.709     0.776       347
         ORG      0.787     0.847     0.816       144
         EVE      0.855     0.925     0.889       134
   micro avg      0.863     0.811     0.836       799
   macro avg      0.863     0.845     0.851       799
weighted avg      0.865     0.811     0.834       799

## EVENT
### Baseline
event options: gaz+postag
                precision    recall  f1-score   support

ACCIDENT-EVENT      1.000     1.000     1.000        25
    FIRE-EVENT      0.806     0.967     0.879        30
   FLOOD-EVENT      0.886     0.861     0.873        36
   QUAKE-EVENT      0.885     0.793     0.836        29
     micro avg      0.885     0.900     0.893       120
     macro avg      0.894     0.905     0.897       120
  weighted avg      0.889     0.900     0.892       120

### Proposed



event options: entity
                  precision    recall  f1-score   support

ACCIDENT-EVENT      0.962     1.000     0.980        25
    FIRE-EVENT      0.968     1.000     0.984        30
   FLOOD-EVENT      1.000     0.972     0.986        36
   QUAKE-EVENT      1.000     1.000     1.000        29
     micro avg      0.983     0.992     0.988       120
     macro avg      0.982     0.993     0.987       120
  weighted avg      0.984     0.992     0.988       120

## ARG
### Baseline

arg options: gaz+postag
                     precision    recall  f1-score   support

    DeathVictim-Arg      0.615     0.381     0.471        42
        Vehicle-Arg      0.625     0.435     0.513        23
         Height-Arg      0.875     0.700     0.778        20
OfficerOfficial-Arg      0.711     0.678     0.694        87
           Time-Arg      0.927     0.962     0.944        79
          Place-Arg      0.873     0.832     0.852       173
         Street-Arg      0.708     0.810     0.756        21
       Strength-Arg      0.952     1.000     0.976        20
          micro avg      0.822     0.766     0.793       465
          macro avg      0.786     0.725     0.748       465
       weighted avg      0.812     0.766     0.785       465

### Proposed
       

arg options: entity+event
                     precision    recall  f1-score   support

    DeathVictim-Arg      0.760     0.905     0.826        42
        Vehicle-Arg      1.000     0.913     0.955        23
         Height-Arg      0.833     1.000     0.909        20
OfficerOfficial-Arg      0.849     0.839     0.844        87
           Time-Arg      1.000     1.000     1.000        79
          Place-Arg      0.900     0.884     0.892       173
         Street-Arg      0.526     0.952     0.678        21
       Strength-Arg      1.000     1.000     1.000        20
          micro avg      0.869     0.912     0.890       465
          macro avg      0.859     0.937     0.888       465
       weighted avg      0.884     0.912     0.894       465

## PLOC
### Baseline

ploc options: gaz+postag

              precision    recall  f1-score   support

        PLOC      0.835     0.784     0.809       116
         LOC      0.528     0.655     0.585        58
   micro avg      0.713     0.741     0.727       174
   macro avg      0.681     0.720     0.697       174
weighted avg      0.733     0.741     0.734       174

### Proposed

       ploc options: ismax+arg+event

              precision    recall  f1-score   support

        PLOC      0.971     0.879     0.923       116
         LOC      0.809     0.948     0.873        58
   micro avg      0.908     0.902     0.905       174
   macro avg      0.890     0.914     0.898       174
weighted avg      0.917     0.902     0.906       174

