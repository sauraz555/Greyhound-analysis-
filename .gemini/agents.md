# Greyhound Edge Engine v3.2 - Agent Registry

This registry defines the core agent archetypes for the Greyhound Edge Engine pipeline.

## 0. orchestrator
**Role**: Master Coordinator
**Description**: Manages the end-to-end analysis pipeline. Takes raw form guide input from the user (plain text or parsed Excel data) and routes it sequentially through the parser, profiler, conflict, mapper, modeler, and report agents. Ensure strict adherence to the A-K output structure.
**Skills Used**: All

## 1. parser_agent
**Role**: Data Ingestion & Validation
**Description**: Extracts raw text/Excel data into a structured format. Verifies that no runners are skipped and that all race metadata is captured. Builds the Section A output.
**Skills Used**: form_extraction, integrity_checker

## 2. profiler_agent
**Role**: Quantitative Feature Analyst
**Description**: Analyzes historical form to build recency-weighted Speed Figures (SF), Ability Scores (AS), Early Speed Ratings (ESR), Mid/Finish Ratings (MFR), and Start Reliability (SR). Computes Freshness decay.
**Skills Used**: speed_profiler, start_reliability

## 3. conflict_agent
**Role**: Context & Pressure Analyst
**Description**: Analyzes the race context. Calculates the Pressure Index (PI) for squeeze boxes, identifies conflict pairs into the first turn, and evaluates class movement (Up/Same/Down).
**Skills Used**: pressure_conflict, class_movement

## 4. mapper_agent
**Role**: Race Simulator
**Description**: Synthesizes the profiles and pressure metrics to map out the likely race shape. Builds two distinct scenarios: Scenario A (mainline, 70-80% probability) and Scenario B (the jam/sweep, 20-30% probability).
**Skills Used**: scenario_mapper

## 5. modeler_agent
**Role**: Probability & Value Engine
**Description**: Takes the simulated scenarios and converts them into normalized Win%, Top3%, and Top4% probabilities. Compares these to market odds to find value bets based on strict edges (Win 12%, Place 8%, Top4 6%). Applies the false-fav filter.
**Skills Used**: probability_engine, value_classifier

## 6. report_agent
**Role**: Final Output Assembler
**Description**: Assembles the findings from all previous agents into the final A-K structured markdown report. Responsible for formatting the required picks, exotics builder (Trifecta/First4), and one-screen summary.
**Skills Used**: All (read-only)
