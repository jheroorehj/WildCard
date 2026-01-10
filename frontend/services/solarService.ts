import { InvestmentFormData, AnalysisResult } from "../types";

const UPSTAGE_API_KEY = process.env.UPSTAGE_API_KEY || '';
const UPSTAGE_API_URL = 'https://api.upstage.ai/v1/solar/chat/completions';

export const analyzeInvestmentLoss = async (data: InvestmentFormData): Promise<AnalysisResult> => {
  const prompt = `
    다음 투자 손실 시나리오를 분석해주세요:
    종목명: ${data.stockName}
    매수일: ${data.buyDate}
    매도일: ${data.sellDate}
    결정 근거: ${data.decisionBasis.join(", ")}

    전문 투자 분석가의 관점에서 다음 사항을 분석해주세요:
    1. 손실이 발생한 주요 원인 분석
    2. 해당 기간의 기술적 시장 상황
    3. 맞춤형 학습 경로 제안 (제목, 설명, 실행 항목 포함)
    4. 행동 투자 가이드
    5. 3개의 후속 질문 제안

    응답은 반드시 다음 JSON 형식으로 제공해주세요:
    {
      "reason": "손실 원인 분석",
      "technicalAnalysis": "기술적 시장 맥락",
      "learningPath": {
        "title": "학습 경로 제목",
        "description": "학습 경로 설명",
        "actionItems": ["실행 항목 1", "실행 항목 2", "실행 항목 3"]
      },
      "behavioralGuide": "행동 투자 조언",
      "suggestedQuestions": ["질문 1", "질문 2", "질문 3"]
    }
  `;

  const response = await fetch(UPSTAGE_API_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${UPSTAGE_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'solar-pro-2',
      messages: [
        {
          role: 'system',
          content: 'You are a professional investment analyst. Provide detailed, structured analysis in Korean. Always respond in valid JSON format.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: 0.7,
    }),
  });

  if (!response.ok) {
    throw new Error(`Upstage API error: ${response.statusText}`);
  }

  const result = await response.json();
  const content = result.choices[0].message.content;

  // Extract JSON from markdown code blocks if present
  const jsonMatch = content.match(/```json\n?([\s\S]*?)\n?```/) || content.match(/\{[\s\S]*\}/);
  const jsonString = jsonMatch ? (jsonMatch[1] || jsonMatch[0]) : content;

  return JSON.parse(jsonString);
};

export const chatWithAnalyst = async (history: {role: string, content: string}[], message: string) => {
  const messages = [
    {
      role: 'system',
      content: 'You are a senior investment advisor. Help the user learn from their losses. Keep answers structured and empathetic but professional. Answer in Korean.'
    },
    ...history.map(h => ({
      role: h.role === 'user' ? 'user' : 'assistant',
      content: h.content
    })),
    {
      role: 'user',
      content: message
    }
  ];

  const response = await fetch(UPSTAGE_API_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${UPSTAGE_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'solar-pro-2',
      messages,
      temperature: 0.7,
    }),
  });

  if (!response.ok) {
    throw new Error(`Upstage API error: ${response.statusText}`);
  }

  const result = await response.json();
  return result.choices[0].message.content;
};
