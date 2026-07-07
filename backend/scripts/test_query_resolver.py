from dataclasses import dataclass
import core.conversation.query_resolver as query_resolver_module
from core.conversation.query_resolver import QueryResolver


def make_signature(query: str, history: list[dict]) -> str:
    history_bits = " | ".join(
        f"{message['role']}:{message['content']}"
        for message in history
    )

    return f"{query}||{history_bits}"


def run_case(
    resolver: QueryResolver,
    title: str,
    query: str,
    history: list[dict],
):
    print("=" * 80)
    print(title)
    print("-" * 80)
    print("Original Query:")
    print(query)

    print("\nHistory:")
    if not history:
        print("(empty)")
    else:
        for message in history:
            print(f"{message['role']:>10}: {message['content']}")

    resolved = resolver.resolve(
        query=query,
        history=history,
    )

    print("\nResolved Query:")
    print(resolved)
    print()


@dataclass
class CaseResult:
    case_id: str
    title: str
    query: str
    history: list[dict]
    llm_output: str | None
    finish_reason: str | None
    expected_final: str
    expect_resolution: bool

    def signature(self) -> str:
        return self.case_id


class FakeLLMProvider:
    def __init__(self, output_map: dict[str, dict]):
        self.output_map = output_map
        self.last_messages = None
        self.last_output = ""
        self.last_finish_reason = None
        self.call_count = 0
        self.current_case_id = None

    def generate_with_metadata(
        self,
        messages: list[dict],
        **kwargs,
    ) -> tuple[str, int, dict]:
        self.call_count += 1
        self.last_messages = messages

        case_data = self.output_map.get(self.current_case_id, {})

        output = case_data.get("llm_output", "")
        finish_reason = case_data.get("finish_reason", "stop")
        tokens = case_data.get("tokens", 12)

        self.last_output = output
        self.last_finish_reason = finish_reason

        return output, tokens, {"finish_reason": finish_reason}

    def generate(
        self,
        messages: list[dict],
        **kwargs,
    ) -> tuple[str, int]:
        output, tokens, _ = self.generate_with_metadata(messages, **kwargs)
        return output, tokens


class TestQueryResolver(QueryResolver):
    def __init__(self, provider: FakeLLMProvider):
        super().__init__()
        self._test_provider = provider

    def _rewrite_with_llm(self, query: str, history: list[dict]) -> dict:
        messages = self._build_messages(query=query, history=history)
        self._test_provider.last_messages = messages

        case_data = self._test_provider.output_map.get(
            self._test_provider.current_case_id,
            {},
        )

        raw_output = case_data.get("llm_output", "")
        finish_reason = case_data.get("finish_reason", "stop")
        tokens = case_data.get("tokens", 12)

        self._test_provider.last_output = raw_output
        self._test_provider.last_finish_reason = finish_reason

        return {
            "messages": messages,
            "raw_output": self._normalize_text(raw_output),
            "finish_reason": finish_reason,
            "tokens": tokens,
        }


def history_pair(question: str, answer: str) -> list[dict]:
    return [
        {
            "role": "user",
            "content": question,
        },
        {
            "role": "assistant",
            "content": answer,
        },
    ]


def build_cases() -> list[CaseResult]:
    leave_history = history_pair(
        "What is the leave policy?",
        "Employees receive 20 annual leave days, 12 sick leave days, and 10 public holidays.",
    )

    remote_work_history = history_pair(
        "What is the remote work policy?",
        "Employees may work remotely two days per week with manager approval.",
    )

    onboarding_history = history_pair(
        "What is the onboarding process?",
        "New hires complete paperwork, device setup, and manager orientation.",
    )

    security_history = history_pair(
        "What is the security policy?",
        "MFA is required for all corporate systems and laptops must use disk encryption.",
    )

    probation_history = history_pair(
        "What is the probation policy?",
        "The standard probation period is 90 days.",
    )

    contractor_history = history_pair(
        "What is the contractor policy?",
        "Contractors need sponsor approval and limited system access.",
    )

    engineering_history = history_pair(
        "What is engineering onboarding?",
        "Engineering onboarding covers environment setup, architecture orientation, and code review expectations.",
    )

    hr_history = history_pair(
        "What does HR handle?",
        "HR handles onboarding coordination, benefits enrollment, and policy questions.",
    )

    department_history = history_pair(
        "How are departments structured?",
        "Departments include engineering, HR, operations, finance, and legal.",
    )

    return [
        CaseResult("case-001", "Standalone - Leave policy", "What is the leave policy?",
                   [], None, None, "What is the leave policy?", False),
        CaseResult("case-002", "Standalone - Security policy", "Explain the security policy.",
                   [], None, None, "Explain the security policy.", False),
        CaseResult("case-003", "Standalone - Remote work policy", "What is the remote work policy?",
                   [], None, None, "What is the remote work policy?", False),
        CaseResult("case-004", "Standalone - Onboarding", "How does onboarding work?",
                   [], None, None, "How does onboarding work?", False),
        CaseResult("case-005", "Standalone - Probation", "What is the probation period?",
                   [], None, None, "What is the probation period?", False),
        CaseResult("case-006", "Standalone - Contractors", "What is the contractor policy?",
                   [], None, None, "What is the contractor policy?", False),
        CaseResult("case-007", "Standalone - Department structure", "How are departments structured?",
                   [], None, None, "How are departments structured?", False),
        CaseResult("case-008", "Standalone - Engineering onboarding", "Tell me about engineering onboarding.",
                   [], None, None, "Tell me about engineering onboarding.", False),
        CaseResult("case-009", "Standalone - HR policy question", "Who owns HR policy updates?",
                   [], None, None, "Who owns HR policy updates?", False),
        CaseResult("case-010", "Rewrite - Leave days follow-up", "How many days is that?", leave_history,
                   "How many annual leave days are provided in the leave policy?", "stop", "How many annual leave days are provided in the leave policy?", True),
        CaseResult("case-011", "Rewrite - Remote work eligibility", "Would this apply?", remote_work_history,
                   "Does the remote work policy apply to contractors?", "stop", "Does the remote work policy apply to contractors?", True),
        CaseResult("case-012", "Rewrite - Onboarding duration", "How long does it take?", onboarding_history,
                   "How long does the onboarding process take?", "stop", "How long does the onboarding process take?", True),
        CaseResult("case-013", "Rewrite - Security continuation", "Explain more.", security_history,
                   "Can you explain the security policy in more detail?", "stop", "Can you explain the security policy in more detail?", True),
        CaseResult("case-014", "Rewrite - Probation extension", "Can it be extended?", probation_history,
                   "Can the probation period be extended under the probation policy?", "stop", "Can the probation period be extended under the probation policy?", True),
        CaseResult("case-015", "Rewrite - Contractors follow-up", "Same for contractors?", remote_work_history,
                   "Does the remote work policy also apply to contractors?", "stop", "Does the remote work policy also apply to contractors?", True),
        CaseResult("case-016", "Rewrite - Interns follow-up", "And interns?", leave_history,
                   "Does the leave policy also apply to interns?", "stop", "Does the leave policy also apply to interns?", True),
        CaseResult("case-017", "Rewrite - Before joining", "Before joining?", onboarding_history, "What should an employee do before joining under the onboarding process?",
                   "stop", "What should an employee do before joining under the onboarding process?", True),
        CaseResult("case-018", "Rewrite - After that", "After that?", onboarding_history,
                   "What happens after the onboarding process?", "stop", "What happens after the onboarding process?", True),
        CaseResult("case-019", "Rewrite - What if I resign", "What if I resign?", leave_history,
                   "What happens to unused leave if an employee resigns?", "stop", "What happens to unused leave if an employee resigns?", True),
        CaseResult("case-020", "Rewrite - Continue", "Continue.", security_history, "What additional security policy requirements are there?",
                   "stop", "What additional security policy requirements are there?", True),
        CaseResult("case-021", "Rewrite - What about HR", "What about HR?", engineering_history,
                   "How does the HR onboarding process work?", "stop", "How does the HR onboarding process work?", True),
        CaseResult("case-022", "Rewrite - Long conversation and recent reference", "Who approves it?", department_history + hr_history +
                   onboarding_history, "Who approves the onboarding process?", "stop", "Who approves the onboarding process?", True),
        CaseResult("case-023", "Rewrite - Empty rewrite fallback", "How many days is that?",
                   leave_history, "", "stop", "How many days is that?", True),
        CaseResult("case-024", "Rewrite - Whitespace rewrite fallback", "Would this apply?",
                   remote_work_history, "   ", "stop", "Would this apply?", True),
        CaseResult("case-025", "Rewrite - Refusal fallback", "Explain more.", security_history,
                   "I'm sorry, I can't help with that.", "stop", "Explain more.", True),
        CaseResult("case-026", "Rewrite - JSON fallback", "Can it be extended?", probation_history,
                   '{"query": "probation extension"}', "stop", "Can it be extended?", True),
        CaseResult("case-027", "Rewrite - Markdown fallback", "Same for contractors?", remote_work_history,
                   "- remote work policy\n- contractors", "stop", "Same for contractors?", True),
        CaseResult("case-028", "Rewrite - Same as original fallback", "What about HR?",
                   engineering_history, "What about HR?", "stop", "What about HR?", True),
        CaseResult("case-029", "Rewrite - Finish reason length", "How long does it take?", onboarding_history,
                   "How long does the onboarding process take", "length", "How long does the onboarding process take?", True),
        CaseResult("case-030", "Rewrite - Department follow-up", "Which one?", department_history,
                   "Which department handles access requests?", "stop", "Which department handles access requests?", True),
        CaseResult("case-031", "Rewrite - Short follow-up with policy context", "When?", probation_history,
                   "When does the probation period end?", "stop", "When does the probation period end?", True),
        CaseResult("case-032", "Rewrite - Who is eligible", "Who is eligible?", contractor_history,
                   "Who is eligible under the contractor policy?", "stop", "Who is eligible under the contractor policy?", True),
        CaseResult("case-033", "Rewrite - How about engineering", "How about engineering?", hr_history,
                   "How does the engineering onboarding process work?", "stop", "How does the engineering onboarding process work?", True),
        CaseResult("case-034", "Rewrite - More details", "More details.", security_history,
                   "What are the detailed security policy requirements?", "stop", "What are the detailed security policy requirements?", True),
        CaseResult("case-035", "Rewrite - Expand", "Expand.", onboarding_history,
                   "Can you expand on the onboarding process?", "stop", "Can you expand on the onboarding process?", True),
        CaseResult("case-036", "Rewrite - Ellipsis on policy", "After that, what happens?", leave_history,
                   "What happens after the employee completes the leave process?", "stop", "What happens after the employee completes the leave process?", True),
        CaseResult("case-037", "Rewrite - Follow-up with specific team", "And the finance team?", department_history,
                   "How does the policy apply to the finance team?", "stop", "How does the policy apply to the finance team?", True),
    ]


def run_case(
    resolver: QueryResolver,
    provider: FakeLLMProvider,
    case: CaseResult,
):
    print("=" * 80)
    print(case.title)
    print("-" * 80)
    print("Original Query:")
    print(case.query)

    print("\nHistory:")
    if not case.history:
        print("(empty)")
    else:
        for message in case.history:
            print(f"{message['role']:>10}: {message['content']}")

    provider.current_case_id = case.case_id

    selected_history = resolver._select_history(case.history)
    decision, decision_reason = resolver._resolution_decision(
        case.query,
        case.history,
    )

    resolved = resolver.resolve(
        query=case.query,
        history=case.history,
    )

    if decision:
        raw_rewrite = provider.last_output
        validation_result, validation_reason = resolver._is_valid_rewrite(
            case.query,
            raw_rewrite,
        )
    else:
        raw_rewrite = "(skipped)"
        validation_result = True
        validation_reason = "not_applicable"

    print("\nHistory Used:")
    if not selected_history:
        print("(empty)")
    else:
        for message in selected_history:
            print(f"{message['role']:>10}: {message['content']}")

    print("\nNeeds Resolution:")
    print(f"{decision} ({decision_reason})")

    print("\nRaw Rewrite:")
    print(raw_rewrite)

    print("\nFinish Reason:")
    print(provider.last_finish_reason if decision else "(skipped)")

    print("\nValidation Result:")
    print(f"{validation_result} ({validation_reason})")

    print("\nFinal Rewrite:")
    print(resolved)

    passed = resolved == case.expected_final and decision == case.expect_resolution

    print("\nPASS / FAIL:")
    print("PASS" if passed else "FAIL")
    print()

    return passed


def main():
    cases = build_cases()

    provider_map = {
        case.case_id: {
            "llm_output": case.llm_output or "",
            "finish_reason": case.finish_reason or "stop",
        }
        for case in cases
    }

    provider = FakeLLMProvider(provider_map)
    resolver = TestQueryResolver(provider)

    total = 0
    passed = 0

    for case in cases:
        total += 1
        if run_case(resolver, provider, case):
            passed += 1

    print("=" * 80)
    print(f"Summary: {passed}/{total} cases passed")


if __name__ == "__main__":
    main()


def main():

    resolver = QueryResolver()

    #
    # Case 1
    # Standalone query
    #
    run_case(
        resolver,
        "CASE 1 - Standalone Question",
        "What is onboarding?",
        [],
    )

    #
    # Case 2
    # Pronoun resolution
    #
    history = [
        {
            "role": "user",
            "content": "What is the leave policy?",
        },
        {
            "role": "assistant",
            "content": (
                "Employees receive 20 annual paid leaves, "
                "12 sick leaves and 10 public holidays."
            ),
        },
    ]

    run_case(
        resolver,
        "CASE 2 - Pronoun Resolution",
        "How many days is that?",
        history,
    )

    #
    # Case 3
    #
    run_case(
        resolver,
        "CASE 3 - 'it' reference",
        "Explain it.",
        history,
    )

    #
    # Case 4
    #
    run_case(
        resolver,
        "CASE 4 - 'those' reference",
        "Can those be carried forward?",
        history,
    )

    #
    # Case 5
    #
    onboarding_history = [
        {
            "role": "user",
            "content": "What is onboarding?",
        },
        {
            "role": "assistant",
            "content": (
                "Onboarding is the employee orientation "
                "process that takes one to two weeks."
            ),
        },
    ]

    run_case(
        resolver,
        "CASE 5 - Different Topic",
        "How long does it take?",
        onboarding_history,
    )


if __name__ == "__main__":
    main()
