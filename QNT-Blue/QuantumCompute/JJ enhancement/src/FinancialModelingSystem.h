/*
 * Financial Modeling System for Brain Simulation
 * Header file containing financial modeling functions
 */

#ifndef FINANCIAL_MODELING_SYSTEM_H
#define FINANCIAL_MODELING_SYSTEM_H

#include "NeuralEnhancementSystem.h"

// Function declarations for financial modeling
bool InitializeFinancialModeling(BrainSimulation* simulation, const std::string& codename);
bool CalculateNetWorth(BrainSimulation* simulation, UserStats* stats);
bool ModelBitcoinHoldings(BrainSimulation* simulation);
bool TrackMajorInvestments(BrainSimulation* simulation);
bool SimulateGovernmentContact(BrainSimulation* simulation, UserStats* stats);
bool CalculateEconomicInfluence(BrainSimulation* simulation);
bool TrackFinancialMilestones(BrainSimulation* simulation);
bool GenerateFinancialReport(BrainSimulation* simulation, ProcessorMetrics* metrics);

#endif // FINANCIAL_MODELING_SYSTEM_H