import React from 'react';
import { InvestmentFormData, StockDetail } from '../types';
import { DECISION_OPTIONS, TRADE_PATTERNS, TRADE_PERIODS, ICONS } from '../constants';
import { DateRangePicker } from './DateRangePicker';

interface FormViewProps {
  step: number;
  formData: InvestmentFormData;
  stockInput: string;
  setStockInput: (val: string) => void;
  showCustomPeriod: Record<number, boolean>;
  handleAnalysis: () => void;
  nextStep: () => void;
  prevStep: () => void;
  addStock: () => void;
  removeStock: (name: string) => void;
  updateStockDetail: (index: number, updates: Partial<StockDetail>) => void;
  toggleStockPattern: (index: number, pattern: string) => void;
  toggleDecisionBasis: (option: string) => void;
  toggleCustomInput: (index: number) => void;
  isNextDisabled: boolean;
}

export const FormView: React.FC<FormViewProps> = ({
  step,
  formData,
  stockInput,
  setStockInput,
  showCustomPeriod,
  handleAnalysis,
  nextStep,
  prevStep,
  addStock,
  removeStock,
  updateStockDetail,
  toggleStockPattern,
  toggleDecisionBasis,
  toggleCustomInput,
  isNextDisabled
}) => {
  const nextButton = (
    <button 
      onClick={step === 3 ? handleAnalysis : nextStep} 
      disabled={isNextDisabled} 
      className="w-full bg-blue-600 disabled:bg-slate-800 disabled:opacity-50 text-white p-5 rounded-2xl font-bold flex items-center justify-center gap-2 transition-all active:scale-95 shadow-xl shadow-blue-900/20"
    >
      {step === 3 ? '복기 노트 생성하기' : '다음으로 넘어가기'} {ICONS.ArrowRight}
    </button>
  );

  return (
    <div className="h-screen max-w-md mx-auto bg-slate-950 flex flex-col shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/10 blur-[100px] rounded-full -mr-32 -mt-32"></div>
      
      {/* Fixed Header */}
      <div className="p-8 pb-4 shrink-0 z-20">
        <div className="flex items-center">
          <button onClick={prevStep} className="p-2 -ml-2 text-slate-400 hover:text-white transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m15 18-6-6 6-6"/></svg>
          </button>
          <div className="h-1 flex-1 bg-slate-800 mx-4 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 transition-all duration-500" style={{ width: `${(step / 3) * 100}%` }}></div>
          </div>
          <span className="text-slate-500 font-mono text-xs">{step}/3</span>
        </div>
      </div>

      {step === 2 ? (
        /* Step 2 Only: Integrated Scroll Layout (Title + Content + Button all scroll together) */
        <div className="flex-1 overflow-y-auto px-8 pb-8 custom-scrollbar relative z-10">
          <div className="step-transition animate-in fade-in slide-in-from-bottom-4 flex flex-col">
            <h1 className="text-2xl font-bold mb-1 leading-tight">종목별 <span className="text-blue-400">거래 상황</span>을<br/>알려주세요.</h1>
            <p className="text-slate-500 text-[11px] mb-6 font-medium">기간을 입력하면 시장 상황과 연동하여 더 좋은 결과를 낼 수 있습니다.</p>
            
            <div className="space-y-4 mb-8">
              {formData.stocks.map((stock, idx) => (
                <div key={stock.name} className="bg-slate-900/40 rounded-3xl p-4 border border-slate-800 space-y-4 shadow-sm">
                  <div className="flex justify-between items-center">
                    <h3 className="text-base font-black text-white">{stock.name}</h3>
                    <div className="flex bg-slate-800 p-0.5 rounded-lg shrink-0">
                      <button onClick={() => updateStockDetail(idx, {status: 'holding'})} className={`px-2.5 py-1 text-[9px] font-bold rounded-md transition-all ${stock.status === 'holding' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500'}`}>보유 중</button>
                      <button onClick={() => updateStockDetail(idx, {status: 'sold'})} className={`px-2.5 py-1 text-[9px] font-bold rounded-md transition-all ${stock.status === 'sold' ? 'bg-slate-700 text-white shadow-lg' : 'text-slate-500'}`}>매도 완료</button>
                    </div>
                  </div>

                  <div className="space-y-2.5">
                    <div className="flex justify-between items-center">
                      <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1">언제 거래했나요? {ICONS.Calendar}</p>
                      <button onClick={() => toggleCustomInput(idx)} className={`flex items-center gap-1 px-2 py-0.5 rounded-md text-[8px] font-black uppercase transition-all border ${showCustomPeriod[idx] ? 'bg-blue-600 text-white border-blue-400' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                        {ICONS.Edit} 직접 입력
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {TRADE_PERIODS.map(p => (
                        <button key={p} onClick={() => updateStockDetail(idx, {period: p})} className={`px-2 py-1 rounded-full text-[9px] font-medium border transition-all ${stock.period === p ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'bg-slate-900/50 border-slate-800 text-slate-500'}`}>{p}</button>
                      ))}
                    </div>
                    {showCustomPeriod[idx] && (
                      <div className="space-y-2">
                        <input 
                          type="text" 
                          placeholder="분석 기간 (예: 2024년 여름 등)" 
                          className="w-full bg-slate-950/50 border border-slate-700 rounded-xl px-3 py-2 text-[10px] text-white placeholder:text-slate-700 focus:border-blue-500 outline-none" 
                          value={stock.customPeriod} 
                          onChange={(e) => updateStockDetail(idx, { customPeriod: e.target.value })} 
                        />
                        <DateRangePicker value={stock.customPeriod || ''} onChange={(val) => updateStockDetail(idx, { customPeriod: val })} />
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">매매 패턴 (중복 가능)</p>
                    <div className="flex flex-wrap gap-1">
                      {TRADE_PATTERNS.map(p => (
                        <button key={p} onClick={() => toggleStockPattern(idx, p)} className={`px-2 py-1 rounded-full text-[9px] font-medium border transition-all ${stock.patterns.includes(p) ? 'bg-emerald-600/20 border-emerald-500 text-emerald-400' : 'bg-slate-900/50 border-slate-800 text-slate-500'}`}>{p}</button>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {nextButton}
          </div>
        </div>
      ) : (
        /* Step 1 and 3: Standard Layout (Fixed Button at bottom) */
        <>
          <div className="flex-1 flex flex-col px-8 overflow-hidden relative z-10">
            {step === 1 && (
              <div className="step-transition animate-in fade-in slide-in-from-bottom-4 flex flex-col h-full">
                <h1 className="text-2xl font-bold mb-3 leading-tight shrink-0">이번에 복기할 <br/><span className="text-blue-400">종목은 무엇인가요?</span></h1>
                <p className="text-slate-500 text-xs mb-6 shrink-0">투자 판단을 되돌아보고 싶은 모든 대상을 추가해주세요.</p>
                
                <div className="relative mb-4 h-[56px] bg-slate-900/60 rounded-2xl border border-slate-800 focus-within:border-blue-500 transition-all flex items-center shrink-0">
                  <input type="text" autoFocus placeholder="종목명 입력 (예: 삼성전자)" className="flex-1 h-full bg-transparent pl-5 pr-14 text-base font-bold text-white outline-none placeholder:text-slate-700" value={stockInput} onChange={e => setStockInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && addStock()} />
                  <div className="absolute right-2.5 w-9 h-9 flex items-center justify-center">
                    <button onClick={addStock} className="w-full h-full flex items-center justify-center bg-blue-600 text-white rounded-lg active:scale-95 transition-all shadow-lg">{ICONS.Plus}</button>
                  </div>
                </div>

                {/* Dotted Separator 복구 */}
                <div className="my-2 border-t-2 border-dotted border-slate-800/60 shrink-0"></div>

                <div className="flex-1 overflow-y-auto space-y-2 mb-4 custom-scrollbar">
                  {formData.stocks.map(stock => (
                    <div key={stock.name} className="relative h-[56px] bg-slate-900/60 rounded-2xl flex items-center border border-slate-800 animate-in slide-in-from-top-2 shrink-0">
                      <span className="flex-1 pl-5 text-base font-bold text-white truncate">{stock.name}</span>
                      <button onClick={() => removeStock(stock.name)} className="absolute right-2.5 w-9 h-9 flex items-center justify-center bg-slate-800/80 text-slate-500 rounded-lg">{ICONS.Minus}</button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="step-transition animate-in fade-in slide-in-from-bottom-4 flex flex-col h-full">
                <h1 className="text-2xl font-bold mb-6 leading-tight shrink-0">투자 결정의 <span className="text-blue-400">핵심 근거</span>는<br/>무엇이었나요?</h1>
                <div className="flex-1 overflow-y-auto space-y-3 mb-4 custom-scrollbar pr-1">
                  {DECISION_OPTIONS.map(option => (
                    <button key={option} onClick={() => toggleDecisionBasis(option)} className={`w-full p-4 rounded-2xl text-left transition-all border ${formData.decisionBasis.includes(option) ? 'bg-blue-600 border-blue-400 text-white shadow-lg' : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'}`}>
                      <div className="flex justify-between items-center"><span className="font-medium text-sm">{option}</span>{formData.decisionBasis.includes(option) && ICONS.Check}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
          {/* Fixed Footer for Step 1 and 3 */}
          <div className="p-8 pt-2 shrink-0 relative z-20">
            {nextButton}
          </div>
        </>
      )}
    </div>
  );
};