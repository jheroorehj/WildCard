
export interface InvestmentFormData {
  stockName: string;
  buyDate: string;
  sellDate: string;
  decisionBasis: string[];
}

export interface AnalysisResult {
  reason: string;
  technicalAnalysis: string;
  learningPath: {
    title: string;
    description: string;
    actionItems: string[];
  };
  behavioralGuide: string;
  suggestedQuestions: string[];
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}
