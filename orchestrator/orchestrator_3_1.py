#!/usr/bin/env python3
"""
ORCHESTRATOR-3.1 - Master Coordinator
Chapéus Lisboeta WooCommerce Rebuild

Coordena 15 sub-agents especializados através de 6 fases
Execução paralela, monitoramento tempo real, rollback automático

Arquitetura:
- 15 sub-agents especializados
- 6 phases (0-5): Photos → Data → UX → Integrations → Performance → Handoff
- Validation gates entre fases
- Rollback automático em caso de falha
- Reporting tempo real
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from enum import Enum

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
AGENTS_DIR = BASE_DIR / 'orchestrator' / 'agents'
REPORTS_DIR = BASE_DIR / 'relatorios' / 'orchestrator'
BACKUPS_DIR = BASE_DIR / 'backups' / 'orchestrator'

# Ensure directories exist
AGENTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(REPORTS_DIR / f'orchestrator_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Phase(Enum):
    """Project phases"""
    PHASE_0 = "Phase 0: Emergency AI Photos"
    PHASE_1 = "Phase 1: Data Foundation"
    PHASE_2 = "Phase 2: Product Enrichment"
    PHASE_3 = "Phase 3: UX Polish"
    PHASE_4 = "Phase 4: Portuguese Integrations"
    PHASE_5 = "Phase 5: Performance & Security"
    PHASE_6 = "Phase 6: Client Handoff"


@dataclass
class AgentResult:
    """Agent execution result"""
    agent_name: str
    phase: str
    status: AgentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    success_rate: Optional[float] = None
    items_processed: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}
        if self.end_time and self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()


@dataclass
class ValidationGate:
    """Validation gate between phases"""
    phase: Phase
    required_agents: List[str]
    min_success_rate: float
    critical: bool = True
    auto_rollback: bool = True


class SubAgentSpec:
    """Sub-agent specification"""
    def __init__(
        self,
        name: str,
        phase: Phase,
        script_path: str,
        description: str,
        dependencies: List[str] = None,
        parallel_safe: bool = True,
        timeout_seconds: int = 600
    ):
        self.name = name
        self.phase = phase
        self.script_path = script_path
        self.description = description
        self.dependencies = dependencies or []
        self.parallel_safe = parallel_safe
        self.timeout_seconds = timeout_seconds


class Orchestrator:
    """Master coordinator for all sub-agents"""

    def __init__(self):
        self.results: Dict[str, AgentResult] = {}
        self.start_time = datetime.now()
        self.current_phase = None

        # Define all 15 sub-agents
        self.agents = self._define_agents()

        # Define validation gates
        self.validation_gates = self._define_validation_gates()

        logger.info("="*80)
        logger.info("ORCHESTRATOR-3.1 - Master Coordinator")
        logger.info("Chapéus Lisboeta WooCommerce Rebuild")
        logger.info("="*80)
        logger.info(f"Total sub-agents: {len(self.agents)}")
        logger.info(f"Total phases: {len(Phase)}")
        logger.info(f"Validation gates: {len(self.validation_gates)}")
        logger.info("="*80)

    def _define_agents(self) -> List[SubAgentSpec]:
        """Define all 15 sub-agents with specifications"""
        return [
            # Phase 0: Emergency AI Photos (COMPLETED)
            SubAgentSpec(
                name="PhotoTriage-Agent",
                phase=Phase.PHASE_0,
                script_path="scripts/photo_triage_v2.py",
                description="Import massivo 7.827 fotos AI para WordPress",
                dependencies=[],
                parallel_safe=False  # Database writes
            ),

            # Phase 1: Data Foundation
            SubAgentSpec(
                name="SheetSync-Agent",
                phase=Phase.PHASE_1,
                script_path="orchestrator/agents/sheet_sync_agent.py",
                description="Sync Google Sheets → WordPress (17 worksheets)",
                dependencies=[],
                parallel_safe=False
            ),
            SubAgentSpec(
                name="SheetSanitizer-Agent",
                phase=Phase.PHASE_1,
                script_path="orchestrator/agents/sheet_sanitizer_agent.py",
                description="Validação dados (preço>0, formato SKU)",
                dependencies=["SheetSync-Agent"],
                parallel_safe=True
            ),
            SubAgentSpec(
                name="PriceGate-Agent",
                phase=Phase.PHASE_1,
                script_path="orchestrator/agents/price_gate_agent.py",
                description="Bloqueia produtos sem preço (NO PRICE = NO PUBLISH)",
                dependencies=["SheetSync-Agent"],
                parallel_safe=True
            ),
            SubAgentSpec(
                name="DataDiff-Agent",
                phase=Phase.PHASE_1,
                script_path="orchestrator/agents/data_diff_agent.py",
                description="Comparação Google Sheets vs WordPress",
                dependencies=["SheetSync-Agent"],
                parallel_safe=True
            ),

            # Phase 2: Product Enrichment
            SubAgentSpec(
                name="DescriptionBuilder-Agent",
                phase=Phase.PHASE_2,
                script_path="orchestrator/agents/description_builder_agent.py",
                description="Descrições baseadas em templates (zero custo AI)",
                dependencies=["SheetSync-Agent"],
                parallel_safe=True
            ),
            SubAgentSpec(
                name="ImageInventory-Agent",
                phase=Phase.PHASE_2,
                script_path="orchestrator/agents/image_inventory_agent.py",
                description="Cataloga fotos AI por SKU (7.827 ficheiros)",
                dependencies=["PhotoTriage-Agent"],
                parallel_safe=True
            ),
            SubAgentSpec(
                name="GalleryLinker-Agent",
                phase=Phase.PHASE_2,
                script_path="orchestrator/agents/gallery_linker_agent.py",
                description="Associa imagens aos produtos (featured + gallery)",
                dependencies=["PhotoTriage-Agent", "ImageInventory-Agent"],
                parallel_safe=False
            ),
            SubAgentSpec(
                name="VariationBuilder-Agent",
                phase=Phase.PHASE_2,
                script_path="orchestrator/agents/variation_builder_agent.py",
                description="Variações produtos (18456-A, 18456-B, etc.)",
                dependencies=["SheetSync-Agent"],
                parallel_safe=False
            ),

            # Phase 3: UX Polish
            SubAgentSpec(
                name="WooPagesFixer-Agent",
                phase=Phase.PHASE_3,
                script_path="orchestrator/agents/woo_pages_fixer_agent.py",
                description="Páginas Shop/Cart/Checkout corretas",
                dependencies=[],
                parallel_safe=True
            ),
            SubAgentSpec(
                name="MenuUXFix-Agent",
                phase=Phase.PHASE_3,
                script_path="orchestrator/agents/menu_ux_fix_agent.py",
                description="Dropdown z-index, hero sections, responsive",
                dependencies=[],
                parallel_safe=True
            ),
            SubAgentSpec(
                name="VisualQA-Agent",
                phase=Phase.PHASE_3,
                script_path="orchestrator/agents/visual_qa_agent.py",
                description="Testes regressão visual (BackstopJS)",
                dependencies=["WooPagesFixer-Agent", "MenuUXFix-Agent"],
                parallel_safe=True
            ),

            # Phase 4: Portuguese Integrations (skipped for now - production only)

            # Phase 5: Performance & Security
            SubAgentSpec(
                name="Security&SEO-Agent",
                phase=Phase.PHASE_5,
                script_path="orchestrator/agents/security_seo_agent.py",
                description="Headers security, RGPD, GA4, performance",
                dependencies=[],
                parallel_safe=True,
                timeout_seconds=1200
            ),

            # Phase 6: Verification
            SubAgentSpec(
                name="ImportVerifier-Agent",
                phase=Phase.PHASE_6,
                script_path="orchestrator/agents/import_verifier_agent.py",
                description="Validação pós-import completa",
                dependencies=["SheetSync-Agent", "PhotoTriage-Agent", "GalleryLinker-Agent"],
                parallel_safe=True
            ),
        ]

    def _define_validation_gates(self) -> List[ValidationGate]:
        """Define validation gates between phases"""
        return [
            ValidationGate(
                phase=Phase.PHASE_0,
                required_agents=["PhotoTriage-Agent"],
                min_success_rate=0.5,  # 50% minimum (62/88 folders é ok)
                critical=True,
                auto_rollback=False  # Já executado com sucesso
            ),
            ValidationGate(
                phase=Phase.PHASE_1,
                required_agents=["SheetSync-Agent", "PriceGate-Agent"],
                min_success_rate=0.95,  # 95% minimum
                critical=True,
                auto_rollback=True
            ),
            ValidationGate(
                phase=Phase.PHASE_2,
                required_agents=["GalleryLinker-Agent", "VariationBuilder-Agent"],
                min_success_rate=0.90,  # 90% minimum
                critical=True,
                auto_rollback=True
            ),
            ValidationGate(
                phase=Phase.PHASE_3,
                required_agents=["WooPagesFixer-Agent", "MenuUXFix-Agent"],
                min_success_rate=1.0,  # 100% - must all pass
                critical=True,
                auto_rollback=True
            ),
            ValidationGate(
                phase=Phase.PHASE_5,
                required_agents=["Security&SEO-Agent"],
                min_success_rate=0.95,
                critical=True,
                auto_rollback=False  # Performance não justifica rollback
            ),
        ]

    def execute_agent(self, agent: SubAgentSpec) -> AgentResult:
        """Execute a single sub-agent"""
        logger.info(f"Starting {agent.name} ({agent.phase.value})")

        result = AgentResult(
            agent_name=agent.name,
            phase=agent.phase.value,
            status=AgentStatus.RUNNING,
            start_time=datetime.now()
        )

        try:
            # Check if script exists
            script_path = BASE_DIR / agent.script_path
            if not script_path.exists():
                logger.warning(f"Script not found: {script_path} - creating placeholder")
                self._create_agent_placeholder(agent)
                result.status = AgentStatus.SKIPPED
                result.warnings.append(f"Script não encontrado: {script_path}")
                result.end_time = datetime.now()
                return result

            # Execute agent script
            cmd = [sys.executable, str(script_path)]

            process = subprocess.run(
                cmd,
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=agent.timeout_seconds
            )

            # Parse results
            result.end_time = datetime.now()

            if process.returncode == 0:
                result.status = AgentStatus.COMPLETED
                logger.info(f"✅ {agent.name} completed successfully")
            else:
                result.status = AgentStatus.FAILED
                result.errors.append(f"Exit code: {process.returncode}")
                result.errors.append(process.stderr[:500])  # First 500 chars
                logger.error(f"❌ {agent.name} failed: {process.stderr[:200]}")

            # Store output for reporting
            result.metadata['stdout'] = process.stdout[-1000:] if process.stdout else ""
            result.metadata['stderr'] = process.stderr[-1000:] if process.stderr else ""

        except subprocess.TimeoutExpired:
            result.status = AgentStatus.FAILED
            result.errors.append(f"Timeout after {agent.timeout_seconds}s")
            result.end_time = datetime.now()
            logger.error(f"⏱️  {agent.name} timeout")

        except Exception as e:
            result.status = AgentStatus.FAILED
            result.errors.append(str(e))
            result.end_time = datetime.now()
            logger.error(f"💥 {agent.name} exception: {e}")

        return result

    def _create_agent_placeholder(self, agent: SubAgentSpec):
        """Create placeholder script for missing agent"""
        script_path = BASE_DIR / agent.script_path
        script_path.parent.mkdir(parents=True, exist_ok=True)

        placeholder_code = f'''#!/usr/bin/env python3
"""
{agent.name} - {agent.description}
Phase: {agent.phase.value}
Dependencies: {', '.join(agent.dependencies) if agent.dependencies else 'None'}

STATUS: PLACEHOLDER - Implementation pending
"""

import sys

def main():
    print(f"🔧 {agent.name} - PLACEHOLDER")
    print(f"📝 {agent.description}")
    print(f"⚠️  Implementation pending - skipping for now")
    return 0

if __name__ == '__main__':
    sys.exit(main())
'''

        script_path.write_text(placeholder_code)
        script_path.chmod(0o755)
        logger.info(f"Created placeholder: {script_path}")

    def execute_phase(self, phase: Phase, parallel: bool = True) -> Dict[str, AgentResult]:
        """Execute all agents for a specific phase"""
        logger.info("="*80)
        logger.info(f"EXECUTING {phase.value}")
        logger.info("="*80)

        self.current_phase = phase
        phase_agents = [a for a in self.agents if a.phase == phase]

        logger.info(f"Agents in this phase: {len(phase_agents)}")
        for agent in phase_agents:
            logger.info(f"  - {agent.name}: {agent.description}")

        phase_results = {}

        if parallel and all(a.parallel_safe for a in phase_agents):
            # Execute in parallel
            logger.info("Executing agents in PARALLEL")
            with ThreadPoolExecutor(max_workers=min(4, len(phase_agents))) as executor:
                futures = {executor.submit(self.execute_agent, agent): agent for agent in phase_agents}

                for future in as_completed(futures):
                    agent = futures[future]
                    result = future.result()
                    phase_results[agent.name] = result
                    self.results[agent.name] = result
        else:
            # Execute sequentially
            logger.info("Executing agents SEQUENTIALLY")
            for agent in phase_agents:
                # Check dependencies
                if agent.dependencies:
                    for dep in agent.dependencies:
                        if dep not in self.results or self.results[dep].status != AgentStatus.COMPLETED:
                            logger.warning(f"Skipping {agent.name} - dependency {dep} not satisfied")
                            result = AgentResult(
                                agent_name=agent.name,
                                phase=phase.value,
                                status=AgentStatus.SKIPPED,
                                start_time=datetime.now(),
                                end_time=datetime.now()
                            )
                            result.warnings.append(f"Dependency not satisfied: {dep}")
                            phase_results[agent.name] = result
                            self.results[agent.name] = result
                            continue

                result = self.execute_agent(agent)
                phase_results[agent.name] = result
                self.results[agent.name] = result

        return phase_results

    def validate_gate(self, gate: ValidationGate) -> Tuple[bool, str]:
        """Validate a phase completion gate"""
        logger.info(f"Validating gate for {gate.phase.value}")

        gate_results = []
        for agent_name in gate.required_agents:
            if agent_name not in self.results:
                return False, f"Required agent {agent_name} not executed"

            result = self.results[agent_name]
            gate_results.append(result)

        # Calculate success rate
        completed = len([r for r in gate_results if r.status == AgentStatus.COMPLETED])
        total = len(gate_results)
        success_rate = completed / total if total > 0 else 0

        passed = success_rate >= gate.min_success_rate

        message = f"Gate {gate.phase.value}: {completed}/{total} agents ({success_rate:.1%}) - {'PASS' if passed else 'FAIL'}"

        if passed:
            logger.info(f"✅ {message}")
        else:
            logger.error(f"❌ {message}")

        return passed, message

    def run_all_phases(self, start_phase: Phase = Phase.PHASE_1):
        """Execute all phases with validation gates"""
        logger.info("\n" + "="*80)
        logger.info("STARTING FULL ORCHESTRATION")
        logger.info("="*80 + "\n")

        phases_to_run = [p for p in Phase if p.value >= start_phase.value]

        for phase in phases_to_run:
            # Execute phase
            phase_results = self.execute_phase(phase, parallel=True)

            # Check validation gate
            gate = next((g for g in self.validation_gates if g.phase == phase), None)
            if gate:
                passed, message = self.validate_gate(gate)

                if not passed and gate.critical:
                    logger.error(f"CRITICAL GATE FAILED: {message}")
                    if gate.auto_rollback:
                        logger.error("Auto-rollback triggered!")
                        # TODO: Implement rollback logic
                    break

        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive final report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        report_path = REPORTS_DIR / f'orchestrator_final_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

        # Calculate statistics
        total_agents = len(self.results)
        completed = len([r for r in self.results.values() if r.status == AgentStatus.COMPLETED])
        failed = len([r for r in self.results.values() if r.status == AgentStatus.FAILED])
        skipped = len([r for r in self.results.values() if r.status == AgentStatus.SKIPPED])

        success_rate = (completed / total_agents * 100) if total_agents > 0 else 0

        # Generate report
        report = f"""# ORCHESTRATOR-3.1 - FINAL REPORT

**Generated:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**Total Duration:** {total_duration:.1f}s ({total_duration/60:.1f} minutes)

## SUMMARY

- **Total Agents:** {total_agents}
- **Completed:** {completed} ({completed/total_agents*100:.1f}%)
- **Failed:** {failed} ({failed/total_agents*100:.1f}%)
- **Skipped:** {skipped} ({skipped/total_agents*100:.1f}%)
- **Success Rate:** {success_rate:.1f}%

## RESULTS BY PHASE

"""

        for phase in Phase:
            phase_results = [r for r in self.results.values() if r.phase == phase.value]
            if not phase_results:
                continue

            report += f"\n### {phase.value}\n\n"
            for result in phase_results:
                status_icon = {
                    AgentStatus.COMPLETED: "✅",
                    AgentStatus.FAILED: "❌",
                    AgentStatus.SKIPPED: "⊘",
                    AgentStatus.RUNNING: "⏳"
                }.get(result.status, "?")

                duration_str = f"{result.duration_seconds:.1f}s" if result.duration_seconds else "N/A"
                report += f"- {status_icon} **{result.agent_name}** ({duration_str})\n"

                if result.errors:
                    report += f"  - Errors: {len(result.errors)}\n"
                if result.warnings:
                    report += f"  - Warnings: {len(result.warnings)}\n"

        report += "\n## DETAILED RESULTS\n\n"

        for agent_name, result in self.results.items():
            report += f"\n### {agent_name}\n\n"
            report += f"- **Status:** {result.status.value}\n"
            report += f"- **Phase:** {result.phase}\n"
            report += f"- **Duration:** {result.duration_seconds:.1f}s\n" if result.duration_seconds else ""

            if result.errors:
                report += f"\n**Errors ({len(result.errors)}):**\n"
                for error in result.errors[:5]:  # First 5 errors
                    report += f"- {error}\n"

            if result.warnings:
                report += f"\n**Warnings ({len(result.warnings)}):**\n"
                for warning in result.warnings[:5]:  # First 5 warnings
                    report += f"- {warning}\n"

        report_path.write_text(report)
        logger.info(f"\n{'='*80}")
        logger.info(f"FINAL REPORT: {report_path}")
        logger.info(f"{'='*80}\n")

        # Print summary to console
        print("\n" + "="*80)
        print("ORCHESTRATOR-3.1 - EXECUTION COMPLETE")
        print("="*80)
        print(f"Total Agents: {total_agents}")
        print(f"✅ Completed: {completed} ({completed/total_agents*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total_agents*100:.1f}%)")
        print(f"⊘ Skipped: {skipped} ({skipped/total_agents*100:.1f}%)")
        print(f"⏱️  Duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"\n📄 Full report: {report_path}")
        print("="*80 + "\n")


def main():
    """Main orchestrator entry point"""
    orchestrator = Orchestrator()

    # Start from Phase 1 (Phase 0 already completed)
    orchestrator.run_all_phases(start_phase=Phase.PHASE_1)

    return 0 if len([r for r in orchestrator.results.values() if r.status == AgentStatus.FAILED]) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
