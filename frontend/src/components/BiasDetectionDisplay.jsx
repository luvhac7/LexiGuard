import React from 'react';

const colorSchemes = {
    red: {
        title: 'text-red-400',
        cardBg: 'bg-red-950/30 border-red-500/30',
        label: 'text-red-300',
        text: 'text-white',
        insightBg: 'bg-red-900/30 border-red-500',
        insightLabel: 'text-red-300',
        insightText: 'text-red-100'
    },
    orange: {
        title: 'text-orange-400',
        cardBg: 'bg-orange-950/30 border-orange-500/30',
        label: 'text-orange-300',
        text: 'text-white',
        insightBg: 'bg-orange-900/30 border-orange-500',
        insightLabel: 'text-orange-300',
        insightText: 'text-orange-100'
    },
    amber: {
        title: 'text-amber-400',
        cardBg: 'bg-amber-950/30 border-amber-500/30',
        label: 'text-amber-300',
        text: 'text-white',
        insightBg: 'bg-amber-900/30 border-amber-500',
        insightLabel: 'text-amber-300',
        insightText: 'text-amber-100'
    },
    yellow: {
        title: 'text-yellow-400',
        cardBg: 'bg-yellow-950/30 border-yellow-500/30',
        label: 'text-yellow-300',
        text: 'text-white',
        insightBg: 'bg-yellow-900/30 border-yellow-500',
        insightLabel: 'text-yellow-300',
        insightText: 'text-yellow-100'
    },
    purple: {
        title: 'text-purple-400',
        cardBg: 'bg-purple-950/30 border-purple-500/30',
        label: 'text-purple-300',
        text: 'text-white',
        insightBg: 'bg-purple-900/30 border-purple-500',
        insightLabel: 'text-purple-300',
        insightText: 'text-purple-100'
    },
    pink: {
        title: 'text-pink-400',
        cardBg: 'bg-pink-950/30 border-pink-500/30',
        label: 'text-pink-300',
        text: 'text-white',
        insightBg: 'bg-pink-900/30 border-pink-500',
        insightLabel: 'text-pink-300',
        insightText: 'text-pink-100'
    }
};

const BiasCard = ({ title, caseAData, caseBData, insight, colorClass = 'red' }) => {
    const colors = colorSchemes[colorClass] || colorSchemes.red;

    return (
        <div className="card animate-fade-in">
            <h3 className={`text-lg font-bold ${colors.title} mb-4`}>{title}</h3>
            <div className="grid md:grid-cols-2 gap-6 mb-4">
                <div className={`${colors.cardBg} border rounded-xl p-4 backdrop-blur-sm`}>
                    <div className={`text-sm font-semibold ${colors.label} mb-2`}>Case A</div>
                    {Object.entries(caseAData || {}).map(([key, value]) => (
                        <div key={key} className="mb-3">
                            <div className={`text-xs font-medium ${colors.label} uppercase mb-1`}>
                                {key.replace(/_/g, ' ')}
                            </div>
                            <div className={`text-sm ${colors.text} leading-relaxed`}>
                                {Array.isArray(value) ? value.join(', ') : value || '—'}
                            </div>
                        </div>
                    ))}
                </div>
                <div className={`${colors.cardBg} border rounded-xl p-4 backdrop-blur-sm`}>
                    <div className={`text-sm font-semibold ${colors.label} mb-2`}>Case B</div>
                    {Object.entries(caseBData || {}).map(([key, value]) => (
                        <div key={key} className="mb-3">
                            <div className={`text-xs font-medium ${colors.label} uppercase mb-1`}>
                                {key.replace(/_/g, ' ')}
                            </div>
                            <div className={`text-sm ${colors.text} leading-relaxed`}>
                                {Array.isArray(value) ? value.join(', ') : value || '—'}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            {insight && (
                <div className={`${colors.insightBg} border-l-4 p-4 rounded backdrop-blur-sm`}>
                    <div className={`text-xs font-semibold ${colors.insightLabel} uppercase mb-1`}>
                        Comparative Insight
                    </div>
                    <div className={`text-sm ${colors.insightText} leading-relaxed`}>{insight}</div>
                </div>
            )}
        </div>
    );
};

const BiasDetectionDisplay = ({ biasData }) => {
    if (!biasData) return null;

    const meta = biasData.meta || {};
    const powerDynamics = biasData.power_dynamics || {};
    const emotionalTemp = biasData.emotional_temperature || {};
    const cognitiveBias = biasData.cognitive_bias || {};
    const missingVoice = biasData.missing_voice || {};
    const legalReasoning = biasData.legal_reasoning || {};
    const sentencingDisparity = biasData.sentencing_disparity || {};

    return (
        <div className="space-y-6">
            {/* Meta Information */}
            {meta.case_a_title && meta.case_b_title && (
                <div className="card-glass bg-gradient-to-r from-red-900/30 to-orange-900/30 border-l-4 border-red-500">
                    <h2 className="text-xl font-bold text-red-300 mb-2">Judicial Bias Analysis</h2>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <span className="font-semibold text-red-400">Case A:</span>{' '}
                            <span className="text-white">{meta.case_a_title}</span>
                        </div>
                        <div>
                            <span className="font-semibold text-red-400">Case B:</span>{' '}
                            <span className="text-white">{meta.case_b_title}</span>
                        </div>
                    </div>
                    {meta.domain_detected && (
                        <div className="mt-2 text-sm">
                            <span className="font-semibold text-red-400">Domain:</span>{' '}
                            <span className="text-white">{meta.domain_detected}</span>
                        </div>
                    )}
                </div>
            )}

            {/* 1. Power Dynamics Bias */}
            <BiasCard
                title="1️⃣ Power Dynamics Bias (Authority & Systemic Forces)"
                caseAData={powerDynamics.case_a}
                caseBData={powerDynamics.case_b}
                insight={powerDynamics.comparative_insight}
                colorClass="red"
            />

            {/* 2. Emotional Temperature */}
            <BiasCard
                title="2️⃣ Emotional Temperature (Linguistic Tone Analysis)"
                caseAData={emotionalTemp.case_a}
                caseBData={emotionalTemp.case_b}
                insight={emotionalTemp.comparative_insight}
                colorClass="orange"
            />

            {/* 3. Cognitive Bias Check */}
            <BiasCard
                title="3️⃣ Cognitive Bias Check (Psychological Biases)"
                caseAData={cognitiveBias.case_a}
                caseBData={cognitiveBias.case_b}
                insight={cognitiveBias.comparative_insight}
                colorClass="amber"
            />

            {/* 4. Missing Voice Analysis */}
            <BiasCard
                title="4️⃣ Missing Voice Analysis (Justice-for-Who Test)"
                caseAData={missingVoice.case_a}
                caseBData={missingVoice.case_b}
                insight={missingVoice.comparative_insight}
                colorClass="yellow"
            />

            {/* 5. Legal Reasoning Structure Bias */}
            <BiasCard
                title="5️⃣ Legal Reasoning Structure Bias (Logic & Framing Analysis)"
                caseAData={legalReasoning.case_a}
                caseBData={legalReasoning.case_b}
                insight={legalReasoning.comparative_insight}
                colorClass="purple"
            />

            {/* 6. Sentencing/Remedy Disparity */}
            <BiasCard
                title="6️⃣ Sentencing / Remedy Disparity Check"
                caseAData={sentencingDisparity.case_a}
                caseBData={sentencingDisparity.case_b}
                insight={sentencingDisparity.comparative_insight}
                colorClass="pink"
            />
        </div>
    );
};

export default BiasDetectionDisplay;
