import { webSearchTool, Agent, AgentInputItem, Runner } from "@openai/agents";
import { OpenAI } from "openai";
import { runGuardrails } from "@openai/guardrails";


// Tool definitions
const webSearchPreview = webSearchTool({
  userLocation: {
    type: "approximate",
    country: undefined,
    region: undefined,
    city: undefined,
    timezone: undefined
  },
  searchContextSize: "medium"
})

// Shared client for guardrails and file search
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Guardrails definitions
const slowdownPolicyConfig = {
  guardrails: [
    {
      name: "Contains PII",
      config: {
        block: true,
        entities: [
          "AU_ABN",
          "AU_ACN",
          "AU_MEDICARE",
          "AU_TFN",
          "CREDIT_CARD",
          "CRYPTO",
          "EMAIL_ADDRESS",
          "ES_NIE",
          "ES_NIF",
          "FI_PERSONAL_IDENTITY_CODE",
          "IBAN_CODE",
          "IN_AADHAAR",
          "IN_PAN",
          "IN_PASSPORT",
          "IN_VEHICLE_REGISTRATION",
          "IN_VOTER",
          "IP_ADDRESS",
          "IT_DRIVER_LICENSE",
          "IT_FISCAL_CODE",
          "IT_IDENTITY_CARD",
          "IT_PASSPORT",
          "IT_VAT_CODE",
          "LOCATION",
          "MEDICAL_LICENSE",
          "NRP",
          "PHONE_NUMBER",
          "PL_PESEL",
          "SG_NRIC_FIN",
          "SG_UEN",
          "UK_NHS",
          "UK_NINO",
          "URL",
          "US_BANK_NUMBER",
          "US_DRIVER_LICENSE",
          "US_ITIN",
          "US_PASSPORT",
          "US_SSN"
        ]
      }
    }
  ]
};
const context = { guardrailLlm: client };

// Guardrails utils
function guardrailsHasTripwire(results) {
    return (results ?? []).some((r) => r?.tripwireTriggered === true);
}

function getGuardrailSafeText(results, fallbackText) {
    // Prefer checked_text as the generic safe/processed text
    for (const r of results ?? []) {
        if (r?.info && ("checked_text" in r.info)) {
            return r.info.checked_text ?? fallbackText;
        }
    }
    // Fall back to PII-specific anonymized_text if present
    const pii = (results ?? []).find((r) => r?.info && "anonymized_text" in r.info);
    return pii?.info?.anonymized_text ?? fallbackText;
}

function buildGuardrailFailOutput(results) {
    const get = (name) => (results ?? []).find((r) => {
          const info = r?.info ?? {};
          const n = (info?.guardrail_name ?? info?.guardrailName);
          return n === name;
        }),
          pii = get("Contains PII"),
          mod = get("Moderation"),
          jb = get("Jailbreak"),
          hal = get("Hallucination Detection"),
          piiCounts = Object.entries(pii?.info?.detected_entities ?? {})
              .filter(([, v]) => Array.isArray(v))
              .map(([k, v]) => k + ":" + v.length),
          thr = jb?.info?.threshold,
          conf = jb?.info?.confidence;

    return {
        pii: {
            failed: (piiCounts.length > 0) || pii?.tripwireTriggered === true,
            ...(piiCounts.length ? { detected_counts: piiCounts } : {}),
            ...(pii?.executionFailed && pii?.info?.error ? { error: pii.info.error } : {}),
        },
        moderation: {
            failed: mod?.tripwireTriggered === true || ((mod?.info?.flagged_categories ?? []).length > 0),
            ...(mod?.info?.flagged_categories ? { flagged_categories: mod.info.flagged_categories } : {}),
            ...(mod?.executionFailed && mod?.info?.error ? { error: mod.info.error } : {}),
        },
        jailbreak: {
            // Rely on runtime-provided tripwire; don't recompute thresholds
            failed: jb?.tripwireTriggered === true,
            ...(jb?.executionFailed && jb?.info?.error ? { error: jb.info.error } : {}),
        },
        hallucination: {
            // Rely on runtime-provided tripwire; don't recompute
            failed: hal?.tripwireTriggered === true,
            ...(hal?.info?.reasoning ? { reasoning: hal.info.reasoning } : {}),
            ...(hal?.info?.hallucination_type ? { hallucination_type: hal.info.hallucination_type } : {}),
            ...(hal?.info?.hallucinated_statements ? { hallucinated_statements: hal.info.hallucinated_statements } : {}),
            ...(hal?.info?.verified_statements ? { verified_statements: hal.info.verified_statements } : {}),
            ...(hal?.executionFailed && hal?.info?.error ? { error: hal.info.error } : {}),
        },
    };
}
const slowdownPass = new Agent({
  name: "Slowdown_Pass",
  instructions: `You are \"Slowdown\" — Users witty wellness companion.
Your mission: help user pace his day, remind them to hydrate, stretch, and breathe.
Speak like a clever friend: playful, empathetic, never nagging. Short replies (1–3 sentences).

Rules:
- At the END of every reply, add exactly one short \"Tip of the moment:\" line.
- Randomly choose one small Tip from Web Search which is available to you from Tools (do not repeat the same tip twice in a row if possible):
- Keep it conversational and encouraging, never preachy.

In the End add note that PII not Identified
`,
  model: "gpt-5",
  tools: [
    webSearchPreview
  ],
  modelSettings: {
    reasoning: {
      effort: "low",
      summary: "auto"
    },
    store: true
  }
});

const slowdownFail = new Agent({
  name: "Slowdown_Fail",
  instructions: `State a message to user that:

PII Identified

-Also tell user to never add PII in chats.
-Do not remember the PII info yourself
`,
  model: "gpt-5",
  modelSettings: {
    reasoning: {
      effort: "low",
      summary: "auto"
    },
    store: true
  }
});

type WorkflowInput = { input_as_text: string };


// Main code entrypoint
export const runWorkflow = async (workflow: WorkflowInput) => {
  const state = {

  };
  const conversationHistory: AgentInputItem[] = [
    {
      role: "user",
      content: [
        {
          type: "input_text",
          text: workflow.input_as_text
        }
      ]
    }
  ];
  const runner = new Runner({
    traceMetadata: {
      __trace_source__: "agent-builder",
      workflow_id: "wf_68e4fac9f2348190a2f27f91d443a5220136d1efe09d5425"
    }
  });
  const guardrailsInputtext = workflow.input_as_text;
  const guardrailsResult = await runGuardrails(guardrailsInputtext, slowdownPolicyConfig, context);
  const guardrailsHastripwire = guardrailsHasTripwire(guardrailsResult);
  const guardrailsAnonymizedtext = getGuardrailSafeText(guardrailsResult, guardrailsInputtext);
  const guardrailsOutput = (guardrailsHastripwire ? buildGuardrailFailOutput(guardrailsResult ?? []) : { safe_text: (guardrailsAnonymizedtext ?? guardrailsInputtext) });
  if (guardrailsHastripwire) {
    const slowdownFailResultTemp = await runner.run(
      slowdownFail,
      [
        ...conversationHistory
      ]
    );
    conversationHistory.push(...slowdownFailResultTemp.newItems.map((item) => item.rawItem));

    if (!slowdownFailResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const slowdownFailResult = {
      output_text: slowdownFailResultTemp.finalOutput ?? ""
    };
  } else {
    const slowdownPassResultTemp = await runner.run(
      slowdownPass,
      [
        ...conversationHistory
      ]
    );
    conversationHistory.push(...slowdownPassResultTemp.newItems.map((item) => item.rawItem));

    if (!slowdownPassResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const slowdownPassResult = {
      output_text: slowdownPassResultTemp.finalOutput ?? ""
    };
  }
}
