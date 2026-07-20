\# York Heat–Health Intelligence Simulator



An interactive geospatial decision-support system for exploring how heatwave conditions and urban greening interventions may influence neighbourhood-level heat-health vulnerability across York, United Kingdom.



\## Project Overview



The York Heat–Health Intelligence Simulator extends an existing GIS-based neighbourhood heat-health vulnerability assessment into an interactive scenario-modelling environment.



Rather than presenting only a static vulnerability map, the application allows users to explore questions such as:



\- How might neighbourhood heat-health vulnerability change under hotter conditions?

\- Which York LSOAs may experience increasing vulnerability?

\- How might increased urban greening alter environmental cooling conditions?

\- Which neighbourhoods remain high priority even after adaptation?

\- Where do neighbourhoods move between Low, Moderate, High and Very High vulnerability classes?



The project follows a decision-support approach:



\*\*Problem → Decision → Factors → Indicators → Data → Analysis → Intelligence → Action\*\*



\---



\## Applications



The repository contains three Streamlit applications.



\### 1. Interactive Intelligence Simulator



Run:



```bash

python -m streamlit run app.py

```



Features include:



\- Heatwave scenario slider from 0°C to +5°C

\- Urban greening intervention slider from 0% to +30%

\- Dynamic recalculation of Heat Hazard

\- Dynamic Environmental Cooling response

\- Scenario HHVI recalculation

\- Low, Moderate, High and Very High vulnerability classes

\- Vulnerability class transitions

\- Improved, stable and worsened neighbourhood counts

\- Interactive York LSOA map

\- Change-from-baseline map

\- Baseline vs Scenario HHVI scatter plot

\- Top 10 scenario-priority neighbourhoods

\- Dominant vulnerability drivers

\- Recommended planning actions



\---



\### 2. Heatwave Animation



Run:



```bash

python -m streamlit run app\_animation.py

```



The animation shows York neighbourhood vulnerability progressing through:



```text

Baseline → +1°C → +2°C → +3°C → +4°C → +5°C

```



The colour scale remains fixed across all animation frames so changes can be compared consistently.



\---



\### 3. Adaptation Comparison Animation



Run:



```bash

python -m streamlit run app\_combined\_animation.py

```



This application provides a synchronised side-by-side comparison of:



```text

Heatwave Only

vs

Heatwave + 30% Urban Greening

```



Both maps progress simultaneously from 0°C to +5°C.



This allows users to compare an unmitigated heatwave scenario with an exploratory urban greening intervention.



\---



\## Heat–Health Vulnerability Framework



The authoritative final baseline output from the original York project is:



```text

HHVI\_Display\_1

```



The validated final index is reconstructed as:



```text

HHVI =

(

&#x20;   Heat Hazard

&#x20;   + Environmental Cooling

&#x20;   + Population Sensitivity

&#x20;   + Social Vulnerability

) / 4

```



The simulator reproduces the original `HHVI\_Display\_1` values for all \*\*121 valid York LSOAs with zero numerical difference\*\* before any scenario changes are applied.



\---



\## Heatwave Scenario Model



The original York analysis showed an exact linear relationship between Land Surface Temperature and the Heat Hazard Index:



```text

Heat Hazard =

0.0506585613 × LST

− 1.12765957

```



Therefore, each +1°C scenario increase changes the Heat Hazard Index by approximately:



```text

+0.05065856

```



Scenario Heat Hazard values are constrained to the original 0–1 index range.



The heatwave slider therefore operates as:



```text

Baseline Heat Hazard

&#x20;       ↓

Add scenario temperature increase

&#x20;       ↓

Recalculate Heat Hazard

&#x20;       ↓

Cap index between 0 and 1

&#x20;       ↓

Recalculate Scenario HHVI

```



\---



\## Urban Greening Scenario



The Environmental Cooling relationship reconstructed from the original York analysis is:



```text

Environmental Cooling =

1.19827236

− (1.81718582 × NDVI)

− (0.00293292 × Park Coverage)

```



In this first simulator version, urban greening is represented as a proportional increase in NDVI.



For example:



```text

+30% Greening

→ Baseline NDVI × 1.30

```



The resulting change in NDVI modifies the Environmental Cooling component and subsequently recalculates HHVI.



The current greening control intentionally modifies only NDVI rather than Park Coverage because the source Park Coverage field contains overlapping-area values above 100% in some LSOAs. This avoids introducing unsupported changes into the scenario model.



The greening scenario is therefore an \*\*exploratory planning scenario\*\*, not a prediction that a specific percentage increase in vegetation will produce an exact real-world reduction in heat-health outcomes.



\---



\## Vulnerability Classes



Fixed thresholds were derived from the quartile distribution of the authoritative baseline field `HHVI\_Display\_1`.



| Vulnerability Class | HHVI Range |

|---|---:|

| Low | ≤ 0.409930 |

| Moderate | > 0.409930 to 0.480659 |

| High | > 0.480659 to 0.553719 |

| Very High | > 0.553719 |



Baseline distribution:



| Class | Number of LSOAs |

|---|---:|

| Low | 31 |

| Moderate | 30 |

| High | 30 |

| Very High | 30 |



The thresholds remain fixed during all simulations.



This is important because recalculating the thresholds after every scenario would hide genuine changes.



Fixed thresholds allow neighbourhoods to move between planning categories such as:



```text

Low → Moderate

Moderate → High

High → Very High



or



Very High → High

High → Moderate

Moderate → Low

```



\---



\## Example Scenario



Under the exploratory scenario:



```text

+3°C Heatwave

+30% Urban Greening

```



the model produced:



```text

Baseline Mean HHVI: 0.492

Scenario Mean HHVI: 0.499

Change: +0.006

```



\### Scenario Vulnerability Classes



```text

Low:        23

Moderate:   33

High:       34

Very High:  31

```



\### Vulnerability Class Transitions



```text

Moved to Lower Class:    2

Stayed in Same Class:  103

Moved to Higher Class:  16

```



The detailed transition matrix showed:



```text

Low → Low:                 23

Low → Moderate:             8



Moderate → Moderate:       24

Moderate → High:            6



High → Moderate:            1

High → High:               27

High → Very High:           2



Very High → High:           1

Very High → Very High:     29

```



This demonstrates why citywide averages alone can hide important neighbourhood-level differences.



Although the average HHVI remained close to baseline, some neighbourhoods still crossed into higher vulnerability categories.



\---



\## Example Adaptation Result



With:



```text

0°C additional heatwave

+30% Urban Greening

```



the simulator produced:



```text

Baseline Mean HHVI: 0.492

Scenario Mean HHVI: 0.462

Change: -0.030

```



Scenario classes changed to:



```text

Low:        45

Moderate:   29

High:       22

Very High:  25

```



Neighbourhood response:



```text

Improved:             110

Little / No Change:    11

Worsened:               0

```



This illustrates how the scenario engine can be used to explore the spatial distribution of potential adaptation benefits.



\---



\## Example Extreme Heat Scenario



Under:



```text

+5°C Heatwave

0% Additional Greening

```



the simulator produced:



```text

Baseline Mean HHVI: 0.492

Scenario Mean HHVI: 0.551

Change: +0.058

```



Scenario vulnerability classes became:



```text

Low:         5

Moderate:   28

High:       35

Very High:  53

```



Neighbourhood response:



```text

Improved:               0

Little / No Change:     4

Worsened:             117

```



This demonstrates how increasing heat exposure can shift large numbers of neighbourhoods into higher vulnerability categories.



\---



\## Priority Neighbourhood Intelligence



The interactive simulator dynamically ranks the ten neighbourhoods with the highest Scenario HHVI.



For each priority neighbourhood, the application provides:



\- Neighbourhood name

\- Baseline HHVI

\- Scenario HHVI

\- Change from baseline

\- Baseline vulnerability class

\- Scenario vulnerability class

\- Dominant vulnerability driver

\- Recommended planning action



Examples of dominant drivers include:



\- Extreme Heat

\- Low Environmental Cooling

\- Socioeconomic Vulnerability

\- High Building Density



Associated actions may include:



\- Increasing shade and cooling infrastructure

\- Expanding tree canopy and green corridors

\- Strengthening community resilience

\- Establishing cooling centres

\- Increasing heat monitoring

\- Providing targeted social support



An important principle is that a neighbourhood can \*\*improve under an intervention and still remain a high priority\*\* because its absolute vulnerability may remain among the highest in York.



\---



\## Interactive Map Views



The main simulator contains two map modes.



\### Scenario HHVI



Displays the absolute simulated heat-health vulnerability of each York LSOA under the selected scenario.



\### Change from Baseline



Displays how vulnerability changes relative to the validated baseline.



The change map uses:



```text

Dark Green

→ Strong improvement



Light Green

→ Moderate improvement



Grey

→ Little or no meaningful change



Orange

→ Moderate worsening



Red

→ Strong worsening

```



This view makes scenario effects easier to identify than relying only on subtle changes in absolute HHVI colours.



\---



\## Baseline vs Scenario Analysis



The Plotly scatter plot compares:



```text

Baseline HHVI

vs

Scenario HHVI

```



Each point represents one York LSOA.



```text

Above the diagonal

→ Vulnerability increased



Below the diagonal

→ Vulnerability decreased



On or close to the diagonal

→ Little change

```



Users can hover over individual points to inspect neighbourhood-specific values.



\---



\## Animated Heatwave Scenario



The dedicated heatwave animation progresses through:



```text

0°C

↓

+1°C

↓

+2°C

↓

+3°C

↓

+4°C

↓

+5°C

```



The colour scale remains fixed across all frames so changes remain directly comparable.



The animation holds the following components constant:



\- Population Sensitivity

\- Social Vulnerability

\- Environmental Cooling



while progressively increasing:



\- Heat Hazard



This isolates the effect of the heatwave scenario within the HHVI framework.



\---



\## Adaptation Comparison Animation



The side-by-side animation compares:



```text

LEFT

Heatwave Only



RIGHT

Heatwave + 30% Urban Greening

```



Both maps progress through the same:



```text

0°C → +1°C → +2°C → +3°C → +4°C → +5°C

```



Both maps use the same fixed HHVI scale.



This allows the user to visually compare:



```text

No Adaptation

vs

Greening Intervention

```



at every heatwave level.



\---



\## Decision-Support Purpose



The simulator is designed to support questions such as:



\- Which neighbourhoods may become more vulnerable during increasingly severe heat conditions?

\- Which neighbourhoods cross into higher vulnerability classes?

\- Where could urban greening potentially provide the greatest benefit?

\- Which neighbourhoods remain high priority even after adaptation?

\- Where should cooling infrastructure be prioritised?

\- Where could tree canopy expansion or green corridors be most useful?

\- Which neighbourhoods may require stronger community resilience or social-support measures?

\- How do citywide averages differ from neighbourhood-level outcomes?



The central decision-support question is:



> \*\*Where should heat-health adaptation resources and interventions be prioritised under different future heat and greening scenarios?\*\*



\---



\## Technology Stack



\- Python

\- Streamlit

\- GeoPandas

\- Pandas

\- NumPy

\- Folium

\- Streamlit-Folium

\- Plotly

\- Branca

\- GeoPackage

\- Git

\- GitHub



\---



\## Project Structure



```text

york-heat-health-intelligence-simulator/

│

├── app.py

│

├── app\_animation.py

│

├── app\_combined\_animation.py

│

├── data/

│   └── york\_heat\_health\_clean.gpkg

│

├── requirements.txt

├── .gitignore

└── README.md

```



\---



\## Installation



Clone the repository:



```bash

git clone https://github.com/OnyekachiBuilds/york-heat-health-intelligence-simulator.git

```



Enter the project directory:



```bash

cd york-heat-health-intelligence-simulator

```



Create a virtual environment:



```bash

python -m venv .venv

```



Activate it on Windows:



```bash

.venv\\Scripts\\activate

```



Install dependencies:



```bash

python -m pip install -r requirements.txt

```



Run the main simulator:



```bash

python -m streamlit run app.py

```



Run the heatwave animation:



```bash

python -m streamlit run app\_animation.py

```



Run the adaptation comparison animation:



```bash

python -m streamlit run app\_combined\_animation.py

```



\---



\## Methodological Note



Missing values in the original analytical layers were handled consistently with the validated final York workflow.



The final display workflow used mean-imputed values where required before calculating the authoritative `HHVI\_Display\_1`.



The reconstructed simulator baseline achieved:



```text

Maximum difference: 0.0

Exact baseline matches: 121 of 121

```



This means the simulator begins from the same validated baseline as the completed York Heat–Health project before scenario changes are applied.



\---



\## Limitations



The simulator should be interpreted as an exploratory scenario and decision-support tool.



Important limitations include:



\- A +1°C to +5°C slider represents an imposed scenario change rather than a climate forecast.

\- The greening scenario is represented through proportional NDVI change.

\- The model does not currently simulate detailed urban microclimate processes.

\- Building geometry, shading, evapotranspiration and wind-flow effects are not physically simulated.

\- Health outcomes are not epidemiologically predicted.

\- Park expansion is not currently simulated directly because the source Park Coverage field requires further refinement.

\- The results should not replace detailed urban-climate modelling, epidemiological analysis or professional public-health assessment.



Future versions could incorporate:



\- Local climate projections

\- Urban canopy modelling

\- Cooling-centre accessibility

\- Tree-canopy scenarios

\- Building morphology

\- Population exposure

\- 3D urban heat analysis

\- Real-time weather feeds

\- More advanced GeoAI modelling



\---



\## Author



\*\*Onyekachi Orji\*\*



Climate \& Environmental Geospatial Intelligence Specialist



GIS | Remote Sensing | GeoAI | Python | Environmental Intelligence



GitHub: \[OnyekachiBuilds](https://github.com/OnyekachiBuilds)



\---



\## Disclaimer



This project is an exploratory geospatial decision-support and portfolio application.



Scenario outputs illustrate how the underlying York Heat–Health Vulnerability framework responds to specified assumptions.



They should not be interpreted as deterministic forecasts, clinical risk predictions, epidemiological predictions or substitutes for detailed urban-climate, public-health or planning assessments.

