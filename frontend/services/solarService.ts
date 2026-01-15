import { InvestmentFormData, AnalysisResult, Quiz } from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const analyzeInvestmentLoss = async (
  data: InvestmentFormData
): Promise<AnalysisResult> => {
  const latestStock = data.stocks[data.stocks.length - 1];
  const [buyDate, sellDate] =
    latestStock?.period === "직접 입력" && latestStock.customPeriod
      ? latestStock.customPeriod.split(" ~ ").map(value => value.trim())
      : ["", ""];

  const response = await fetch(`${API_BASE_URL}/v1/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      layer1_stock: latestStock?.name || "",
      layer2_buy_date: buyDate || "",
      layer2_sell_date: sellDate || "",
      position_status: latestStock?.status || "holding",
      layer3_decision_basis: data.decisionBasis.join(", "),
      // Optional: Send full stock details in metadata for future use
      metadata: {
        stocks: data.stocks
      }
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
};

export const chatWithAnalyst = async (
  history: { role: string; content: string }[],
  message: string
) => {
  const response = await fetch(`${API_BASE_URL}/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      history,
      message,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
};

export const generateInvestmentQuiz = async (
  analysis: AnalysisResult
): Promise<Quiz[]> => {
  const response = await fetch(`${API_BASE_URL}/v1/quiz`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      learning_pattern_analysis: analysis.learning_pattern_analysis || {},
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json();
  const quizzes = data?.quiz_set?.quizzes;
  if (!Array.isArray(quizzes)) {
    return [];
  }

  return quizzes.map((quiz: any) => {
    const type = quiz.quiz_type === "reflection" ? "personality" : "standard";
    const options = Array.isArray(quiz.options)
      ? quiz.options.map((option: any) => {
          if (typeof option === "string") {
            return { text: option };
          }
          return {
            text: String(option?.text || ""),
            solution: option?.solution ? String(option.solution) : undefined,
          };
        })
      : [];
    const correctIndex =
      typeof quiz.correct_answer_index === "number" ? quiz.correct_answer_index : 0;

    return {
      question: String(quiz.question || ""),
      type,
      options,
      correctAnswerIndex: type === "standard" ? correctIndex : undefined,
    } as Quiz;
  });
};
