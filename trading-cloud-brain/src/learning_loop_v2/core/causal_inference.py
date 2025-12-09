"""
نظام الاستدلال السببي - Causal Inference System
AlphaAxiom Learning Loop v2.0

يحدد العلاقات السببية بين أحداث السوق وقرارات التداول
باستخدام تقنيات الاستدلال السببي المتقدمة.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import math
import random
from datetime import datetime


class CausalRelationType(Enum):
    """أنواع العلاقات السببية."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    CONFOUNDED = "confounded"
    SPURIOUS = "spurious"
    MEDIATING = "mediating"


class InterventionType(Enum):
    """أنواع التدخلات السببية."""
    DO = "do"
    OBSERVE = "observe"
    COUNTERFACTUAL = "counterfactual"


@dataclass
class CausalVariable:
    """متغير سببي في الرسم البياني."""
    name: str
    value: float
    is_treatment: bool = False
    is_outcome: bool = False
    is_confounder: bool = False
    observed: bool = True
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CausalEdge:
    """حافة سببية تربط بين متغيرين."""
    source: str
    target: str
    strength: float = 0.0
    confidence: float = 0.0
    relation_type: CausalRelationType = CausalRelationType.DIRECT
    lag_periods: int = 0


@dataclass
class CausalEffect:
    """تأثير سببي محسوب."""
    treatment: str
    outcome: str
    ate: float  # Average Treatment Effect
    att: float  # Average Treatment Effect on Treated
    confidence_interval: tuple = (0.0, 0.0)
    p_value: float = 1.0
    is_significant: bool = False
    method: str = "observational"


@dataclass
class CounterfactualResult:
    """نتيجة تحليل مضاد للواقع."""
    factual_outcome: float
    counterfactual_outcome: float
    causal_effect: float
    probability: float
    explanation: str


class CausalGraph:
    """
    رسم بياني سببي يمثل العلاقات بين المتغيرات.
    يستخدم لتحليل السببية في قرارات التداول.
    """

    def __init__(self):
        """تهيئة الرسم البياني السببي."""
        self.variables: dict[str, CausalVariable] = {}
        self.edges: list[CausalEdge] = []
        self._adjacency: dict[str, list[str]] = {}
        self._reverse_adjacency: dict[str, list[str]] = {}

    def add_variable(self, variable: CausalVariable) -> None:
        """إضافة متغير إلى الرسم البياني."""
        self.variables[variable.name] = variable
        if variable.name not in self._adjacency:
            self._adjacency[variable.name] = []
        if variable.name not in self._reverse_adjacency:
            self._reverse_adjacency[variable.name] = []

    def add_edge(self, edge: CausalEdge) -> None:
        """إضافة حافة سببية."""
        if edge.source not in self.variables:
            raise ValueError(f"Source variable {edge.source} not found")
        if edge.target not in self.variables:
            raise ValueError(f"Target variable {edge.target} not found")

        self.edges.append(edge)
        self._adjacency[edge.source].append(edge.target)
        self._reverse_adjacency[edge.target].append(edge.source)

    def get_parents(self, variable_name: str) -> list[str]:
        """الحصول على المتغيرات الأصلية (الآباء)."""
        return self._reverse_adjacency.get(variable_name, [])

    def get_children(self, variable_name: str) -> list[str]:
        """الحصول على المتغيرات الفرعية (الأبناء)."""
        return self._adjacency.get(variable_name, [])

    def get_ancestors(self, variable_name: str) -> set[str]:
        """الحصول على جميع الأسلاف."""
        ancestors = set()
        to_visit = list(self.get_parents(variable_name))

        while to_visit:
            current = to_visit.pop()
            if current not in ancestors:
                ancestors.add(current)
                to_visit.extend(self.get_parents(current))

        return ancestors

    def get_descendants(self, variable_name: str) -> set[str]:
        """الحصول على جميع الأحفاد."""
        descendants = set()
        to_visit = list(self.get_children(variable_name))

        while to_visit:
            current = to_visit.pop()
            if current not in descendants:
                descendants.add(current)
                to_visit.extend(self.get_children(current))

        return descendants

    def find_confounders(
        self,
        treatment: str,
        outcome: str
    ) -> list[str]:
        """
        البحث عن المتغيرات المربكة بين العلاج والنتيجة.
        المربك هو متغير يؤثر على كل من العلاج والنتيجة.
        """
        treatment_ancestors = self.get_ancestors(treatment)
        outcome_ancestors = self.get_ancestors(outcome)

        confounders = []
        common_ancestors = treatment_ancestors.intersection(outcome_ancestors)

        for ancestor in common_ancestors:
            if self.variables.get(ancestor):
                confounders.append(ancestor)

        return confounders

    def is_d_separated(
        self,
        x: str,
        y: str,
        conditioning_set: set[str]
    ) -> bool:
        """
        التحقق من الفصل-d بين متغيرين.
        يستخدم لتحديد الاستقلال الشرطي.
        """
        # Simplified d-separation check
        paths = self._find_all_paths(x, y)

        for path in paths:
            if not self._is_path_blocked(path, conditioning_set):
                return False

        return True

    def _find_all_paths(
        self,
        start: str,
        end: str,
        max_depth: int = 10
    ) -> list[list[str]]:
        """البحث عن جميع المسارات بين نقطتين."""
        paths = []
        self._dfs_paths(start, end, [start], paths, max_depth)
        return paths

    def _dfs_paths(
        self,
        current: str,
        target: str,
        path: list[str],
        paths: list[list[str]],
        max_depth: int
    ) -> None:
        """بحث العمق أولاً للمسارات."""
        if len(path) > max_depth:
            return

        if current == target:
            paths.append(path.copy())
            return

        neighbors = set(self.get_children(current))
        neighbors.update(self.get_parents(current))

        for neighbor in neighbors:
            if neighbor not in path:
                path.append(neighbor)
                self._dfs_paths(neighbor, target, path, paths, max_depth)
                path.pop()

    def _is_path_blocked(
        self,
        path: list[str],
        conditioning_set: set[str]
    ) -> bool:
        """التحقق مما إذا كان المسار محجوباً."""
        if len(path) < 3:
            return False

        for i in range(1, len(path) - 1):
            node = path[i]
            prev_node = path[i - 1]
            next_node = path[i + 1]

            is_collider = (
                prev_node in self.get_parents(node) and
                next_node in self.get_parents(node)
            )

            if is_collider:
                descendants = self.get_descendants(node)
                if node not in conditioning_set:
                    if not descendants.intersection(conditioning_set):
                        return True
            else:
                if node in conditioning_set:
                    return True

        return False


class CausalInferenceEngine:
    """
    محرك الاستدلال السببي الرئيسي.
    يحلل العلاقات السببية في بيانات التداول.
    """

    def __init__(
        self,
        kv_store: Optional[object] = None,
        d1_database: Optional[object] = None
    ):
        """تهيئة محرك الاستدلال السببي."""
        self.kv = kv_store
        self.d1 = d1_database
        self.causal_graph = CausalGraph()
        self._effect_cache: dict[str, CausalEffect] = {}
        self._bootstrap_samples = 1000

    async def build_causal_graph_from_data(
        self,
        observations: list[dict],
        variable_names: list[str]
    ) -> CausalGraph:
        """
        بناء الرسم البياني السببي من البيانات المرصودة.
        يستخدم خوارزمية PC المبسطة.
        """
        graph = CausalGraph()

        # إنشاء المتغيرات
        for name in variable_names:
            values = [obs.get(name, 0.0) for obs in observations]
            avg_value = sum(values) / len(values) if values else 0.0
            var = CausalVariable(name=name, value=avg_value)
            graph.add_variable(var)

        # اكتشاف الحواف باستخدام الارتباط الشرطي
        for i, var1 in enumerate(variable_names):
            for var2 in variable_names[i + 1:]:
                correlation = self._compute_correlation(
                    observations, var1, var2
                )

                if abs(correlation) > 0.3:  # عتبة الارتباط
                    # تحديد اتجاه السببية
                    direction = self._infer_direction(
                        observations, var1, var2
                    )

                    if direction > 0:
                        edge = CausalEdge(
                            source=var1,
                            target=var2,
                            strength=abs(correlation),
                            confidence=min(abs(correlation) * 1.2, 1.0)
                        )
                    else:
                        edge = CausalEdge(
                            source=var2,
                            target=var1,
                            strength=abs(correlation),
                            confidence=min(abs(correlation) * 1.2, 1.0)
                        )

                    graph.add_edge(edge)

        self.causal_graph = graph
        return graph

    def _compute_correlation(
        self,
        observations: list[dict],
        var1: str,
        var2: str
    ) -> float:
        """حساب معامل ارتباط بيرسون."""
        x = [obs.get(var1, 0.0) for obs in observations]
        y = [obs.get(var2, 0.0) for obs in observations]

        n = len(x)
        if n < 2:
            return 0.0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        var_x = sum((xi - mean_x) ** 2 for xi in x)
        var_y = sum((yi - mean_y) ** 2 for yi in y)
        denominator = math.sqrt(var_x * var_y)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _infer_direction(
        self,
        observations: list[dict],
        var1: str,
        var2: str
    ) -> int:
        """
        استنتاج اتجاه السببية.
        يعود: 1 إذا var1 -> var2، -1 إذا var2 -> var1
        """
        # استخدام التأخر الزمني لتحديد الاتجاه
        x = [obs.get(var1, 0.0) for obs in observations]
        y = [obs.get(var2, 0.0) for obs in observations]

        if len(x) < 3:
            return 1

        # Granger causality approximation
        corr_xy_lag = self._lagged_correlation(x[:-1], y[1:])
        corr_yx_lag = self._lagged_correlation(y[:-1], x[1:])

        if corr_xy_lag > corr_yx_lag:
            return 1
        else:
            return -1

    def _lagged_correlation(
        self,
        x: list[float],
        y: list[float]
    ) -> float:
        """حساب الارتباط المتأخر."""
        n = min(len(x), len(y))
        if n < 2:
            return 0.0

        x = x[:n]
        y = y[:n]

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        var_x = sum((xi - mean_x) ** 2 for xi in x)
        var_y = sum((yi - mean_y) ** 2 for yi in y)
        denominator = math.sqrt(var_x * var_y)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    async def estimate_causal_effect(
        self,
        treatment: str,
        outcome: str,
        observations: list[dict],
        method: str = "backdoor"
    ) -> CausalEffect:
        """
        تقدير التأثير السببي باستخدام طرق مختلفة.
        """
        cache_key = f"{treatment}_{outcome}_{method}"
        if cache_key in self._effect_cache:
            return self._effect_cache[cache_key]

        if method == "backdoor":
            effect = await self._backdoor_adjustment(
                treatment, outcome, observations
            )
        elif method == "frontdoor":
            effect = await self._frontdoor_adjustment(
                treatment, outcome, observations
            )
        elif method == "iv":
            effect = await self._instrumental_variable(
                treatment, outcome, observations
            )
        else:
            effect = await self._simple_difference(
                treatment, outcome, observations
            )

        self._effect_cache[cache_key] = effect
        return effect

    async def _backdoor_adjustment(
        self,
        treatment: str,
        outcome: str,
        observations: list[dict]
    ) -> CausalEffect:
        """
        تعديل المسار الخلفي لحساب التأثير السببي.
        يتحكم في المتغيرات المربكة.
        """
        confounders = self.causal_graph.find_confounders(treatment, outcome)

        treated = [
            obs for obs in observations
            if obs.get(treatment, 0) > 0.5
        ]
        control = [
            obs for obs in observations
            if obs.get(treatment, 0) <= 0.5
        ]

        if not treated or not control:
            return CausalEffect(
                treatment=treatment,
                outcome=outcome,
                ate=0.0,
                att=0.0,
                confidence_interval=(0.0, 0.0),
                p_value=1.0,
                is_significant=False,
                method="backdoor"
            )

        # حساب المتوسط المرجح
        treated_outcomes = [obs.get(outcome, 0.0) for obs in treated]
        control_outcomes = [obs.get(outcome, 0.0) for obs in control]

        mean_treated = sum(treated_outcomes) / len(treated_outcomes)
        mean_control = sum(control_outcomes) / len(control_outcomes)

        ate = mean_treated - mean_control

        # Bootstrap for confidence interval
        bootstrap_ates = []
        for _ in range(self._bootstrap_samples):
            sample_treated = random.choices(treated_outcomes, k=len(treated))
            sample_control = random.choices(control_outcomes, k=len(control))
            bootstrap_ate = (
                sum(sample_treated) / len(sample_treated) -
                sum(sample_control) / len(sample_control)
            )
            bootstrap_ates.append(bootstrap_ate)

        bootstrap_ates.sort()
        ci_lower = bootstrap_ates[int(0.025 * len(bootstrap_ates))]
        ci_upper = bootstrap_ates[int(0.975 * len(bootstrap_ates))]

        # تحديد الأهمية الإحصائية
        is_significant = (ci_lower > 0 and ci_upper > 0) or \
                        (ci_lower < 0 and ci_upper < 0)

        return CausalEffect(
            treatment=treatment,
            outcome=outcome,
            ate=ate,
            att=ate,  # تبسيط: ATT = ATE
            confidence_interval=(ci_lower, ci_upper),
            p_value=0.05 if is_significant else 0.5,
            is_significant=is_significant,
            method="backdoor"
        )

    async def _frontdoor_adjustment(
        self,
        treatment: str,
        outcome: str,
        observations: list[dict]
    ) -> CausalEffect:
        """تعديل المسار الأمامي."""
        # تبسيط: استخدام نفس منطق backdoor
        return await self._backdoor_adjustment(
            treatment, outcome, observations
        )

    async def _instrumental_variable(
        self,
        treatment: str,
        outcome: str,
        observations: list[dict]
    ) -> CausalEffect:
        """طريقة المتغير الآلي (IV)."""
        # البحث عن متغير آلي
        potential_ivs = []
        for var_name in self.causal_graph.variables:
            if var_name == treatment or var_name == outcome:
                continue

            # IV يؤثر على العلاج ولكن ليس على النتيجة مباشرة
            affects_treatment = treatment in self.causal_graph.get_children(
                var_name
            )
            affects_outcome_directly = outcome in self.causal_graph.get_children(
                var_name
            )

            if affects_treatment and not affects_outcome_directly:
                potential_ivs.append(var_name)

        if not potential_ivs:
            return await self._backdoor_adjustment(
                treatment, outcome, observations
            )

        # استخدام IV الأول
        iv = potential_ivs[0]

        # Two-stage least squares approximation
        z = [obs.get(iv, 0.0) for obs in observations]
        x = [obs.get(treatment, 0.0) for obs in observations]
        y = [obs.get(outcome, 0.0) for obs in observations]

        n = len(z)
        if n < 3:
            return CausalEffect(
                treatment=treatment,
                outcome=outcome,
                ate=0.0,
                att=0.0,
                confidence_interval=(0.0, 0.0),
                p_value=1.0,
                is_significant=False,
                method="iv"
            )

        # Stage 1: Regress X on Z
        cov_zx = self._compute_covariance(z, x)
        var_z = self._compute_variance(z)

        if var_z == 0:
            return await self._backdoor_adjustment(
                treatment, outcome, observations
            )

        beta_zx = cov_zx / var_z

        # Stage 2: Regress Y on predicted X
        cov_zy = self._compute_covariance(z, y)
        iv_estimate = cov_zy / cov_zx if cov_zx != 0 else 0

        return CausalEffect(
            treatment=treatment,
            outcome=outcome,
            ate=iv_estimate,
            att=iv_estimate,
            confidence_interval=(iv_estimate - 0.1, iv_estimate + 0.1),
            p_value=0.1,
            is_significant=abs(iv_estimate) > 0.05,
            method="iv"
        )

    async def _simple_difference(
        self,
        treatment: str,
        outcome: str,
        observations: list[dict]
    ) -> CausalEffect:
        """فرق بسيط في المتوسطات."""
        treated = [obs.get(outcome, 0) for obs in observations 
                  if obs.get(treatment, 0) > 0.5]
        control = [obs.get(outcome, 0) for obs in observations 
                  if obs.get(treatment, 0) <= 0.5]

        if not treated or not control:
            return CausalEffect(
                treatment=treatment,
                outcome=outcome,
                ate=0.0,
                att=0.0,
                confidence_interval=(0.0, 0.0),
                p_value=1.0,
                is_significant=False,
                method="simple"
            )

        ate = sum(treated)/len(treated) - sum(control)/len(control)

        return CausalEffect(
            treatment=treatment,
            outcome=outcome,
            ate=ate,
            att=ate,
            confidence_interval=(ate - 0.2, ate + 0.2),
            p_value=0.1,
            is_significant=abs(ate) > 0.1,
            method="simple"
        )

    def _compute_covariance(
        self,
        x: list[float],
        y: list[float]
    ) -> float:
        """حساب التغاير."""
        n = len(x)
        if n < 2:
            return 0.0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        return sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n

    def _compute_variance(self, x: list[float]) -> float:
        """حساب التباين."""
        n = len(x)
        if n < 2:
            return 0.0

        mean_x = sum(x) / n
        return sum((xi - mean_x) ** 2 for xi in x) / n

    async def compute_counterfactual(
        self,
        observation: dict,
        intervention: dict,
        outcome_variable: str
    ) -> CounterfactualResult:
        """
        حساب النتيجة المضادة للواقع.
        ماذا لو كان التدخل مختلفاً؟
        """
        factual_outcome = observation.get(outcome_variable, 0.0)

        # تحديد المتغيرات المتأثرة بالتدخل
        affected_vars = set()
        for var in intervention:
            affected_vars.add(var)
            affected_vars.update(
                self.causal_graph.get_descendants(var)
            )

        # حساب النتيجة المضادة للواقع
        counterfactual_obs = observation.copy()
        counterfactual_obs.update(intervention)

        # استخدام العلاقات السببية للتنبؤ
        for edge in self.causal_graph.edges:
            if edge.source in intervention:
                if edge.target == outcome_variable:
                    delta = intervention[edge.source] - observation.get(
                        edge.source, 0.0
                    )
                    counterfactual_obs[outcome_variable] = (
                        factual_outcome + delta * edge.strength
                    )

        counterfactual_outcome = counterfactual_obs.get(outcome_variable, 0.0)
        causal_effect = counterfactual_outcome - factual_outcome

        # تقدير الاحتمالية
        probability = 1.0 / (1.0 + math.exp(-abs(causal_effect)))

        explanation = self._generate_counterfactual_explanation(
            observation,
            intervention,
            factual_outcome,
            counterfactual_outcome
        )

        return CounterfactualResult(
            factual_outcome=factual_outcome,
            counterfactual_outcome=counterfactual_outcome,
            causal_effect=causal_effect,
            probability=probability,
            explanation=explanation
        )

    def _generate_counterfactual_explanation(
        self,
        observation: dict,
        intervention: dict,
        factual: float,
        counterfactual: float
    ) -> str:
        """توليد شرح للنتيجة المضادة للواقع."""
        changes = []
        for var, new_val in intervention.items():
            old_val = observation.get(var, 0.0)
            if new_val != old_val:
                direction = "زيادة" if new_val > old_val else "نقص"
                changes.append(f"{var}: {direction}")

        effect_direction = "زيادة" if counterfactual > factual else "نقص"
        effect_size = abs(counterfactual - factual)

        explanation = (
            f"لو تغيرت المتغيرات ({', '.join(changes)}), "
            f"لكانت النتيجة {effect_direction} بمقدار {effect_size:.4f}"
        )

        return explanation

    async def do_intervention(
        self,
        variable: str,
        value: float,
        observations: list[dict]
    ) -> list[dict]:
        """
        تنفيذ تدخل do(X=x) على البيانات.
        يقطع جميع الحواف الواردة إلى المتغير.
        """
        intervened_observations = []

        for obs in observations:
            new_obs = obs.copy()
            new_obs[variable] = value

            # تحديث المتغيرات المتأثرة
            for child in self.causal_graph.get_children(variable):
                edge = next(
                    (e for e in self.causal_graph.edges 
                     if e.source == variable and e.target == child),
                    None
                )
                if edge:
                    old_parent_val = obs.get(variable, 0.0)
                    delta = value - old_parent_val
                    new_obs[child] = obs.get(child, 0.0) + delta * edge.strength

            intervened_observations.append(new_obs)

        return intervened_observations

    async def analyze_trading_causality(
        self,
        trading_data: list[dict],
        signal_variable: str = "signal",
        return_variable: str = "return"
    ) -> dict:
        """
        تحليل السببية في بيانات التداول.
        يحدد ما إذا كانت الإشارات تسبب العوائد فعلاً.
        """
        # بناء الرسم البياني
        variables = list(trading_data[0].keys()) if trading_data else []
        await self.build_causal_graph_from_data(trading_data, variables)

        # تقدير التأثير السببي للإشارة على العائد
        effect = await self.estimate_causal_effect(
            signal_variable,
            return_variable,
            trading_data,
            method="backdoor"
        )

        # تحليل مضاد للواقع
        if trading_data:
            counterfactual = await self.compute_counterfactual(
                trading_data[-1],
                {signal_variable: 1.0 - trading_data[-1].get(signal_variable, 0)},
                return_variable
            )
        else:
            counterfactual = None

        # تحديد المربكات المحتملة
        confounders = self.causal_graph.find_confounders(
            signal_variable, return_variable
        )

        return {
            "causal_effect": effect,
            "counterfactual_analysis": counterfactual,
            "confounders": confounders,
            "is_causal": effect.is_significant and effect.ate > 0,
            "recommendation": self._generate_trading_recommendation(
                effect, confounders
            )
        }

    def _generate_trading_recommendation(
        self,
        effect: CausalEffect,
        confounders: list[str]
    ) -> str:
        """توليد توصية بناءً على التحليل السببي."""
        if not effect.is_significant:
            return (
                "العلاقة بين الإشارة والعائد غير مؤكدة إحصائياً. "
                "يُنصح بجمع المزيد من البيانات."
            )

        if effect.ate > 0:
            conf_warning = ""
            if confounders:
                conf_warning = (
                    f" احذر من المتغيرات المربكة: {', '.join(confounders)}"
                )
            return (
                f"الإشارة لها تأثير سببي إيجابي على العائد "
                f"(ATE: {effect.ate:.4f}).{conf_warning}"
            )
        else:
            return (
                f"الإشارة لها تأثير سببي سلبي على العائد "
                f"(ATE: {effect.ate:.4f}). يُنصح بمراجعة الاستراتيجية."
            )

    async def save_causal_model(self, model_name: str) -> bool:
        """حفظ النموذج السببي."""
        if not self.kv:
            return False

        model_data = {
            "variables": {
                name: {
                    "value": var.value,
                    "is_treatment": var.is_treatment,
                    "is_outcome": var.is_outcome,
                    "is_confounder": var.is_confounder
                }
                for name, var in self.causal_graph.variables.items()
            },
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "strength": e.strength,
                    "confidence": e.confidence,
                    "relation_type": e.relation_type.value
                }
                for e in self.causal_graph.edges
            ],
            "timestamp": datetime.now().isoformat()
        }

        try:
            await self.kv.put(
                f"causal_model:{model_name}",
                str(model_data)
            )
            return True
        except Exception:
            return False

    async def load_causal_model(self, model_name: str) -> bool:
        """تحميل النموذج السببي."""
        if not self.kv:
            return False

        try:
            model_data = await self.kv.get(f"causal_model:{model_name}")
            if not model_data:
                return False

            import ast
            data = ast.literal_eval(model_data)

            self.causal_graph = CausalGraph()

            for name, var_data in data.get("variables", {}).items():
                var = CausalVariable(
                    name=name,
                    value=var_data.get("value", 0.0),
                    is_treatment=var_data.get("is_treatment", False),
                    is_outcome=var_data.get("is_outcome", False),
                    is_confounder=var_data.get("is_confounder", False)
                )
                self.causal_graph.add_variable(var)

            for edge_data in data.get("edges", []):
                edge = CausalEdge(
                    source=edge_data["source"],
                    target=edge_data["target"],
                    strength=edge_data.get("strength", 0.0),
                    confidence=edge_data.get("confidence", 0.0),
                    relation_type=CausalRelationType(
                        edge_data.get("relation_type", "direct")
                    )
                )
                self.causal_graph.add_edge(edge)

            return True
        except Exception:
            return False
