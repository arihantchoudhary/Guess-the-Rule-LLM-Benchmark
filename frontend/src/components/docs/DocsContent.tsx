import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface DocsContentProps {
  selectedSection: string | null;
  contentRefs: Record<string, React.RefObject<HTMLDivElement>>;
  helpful: boolean | null;
  handleFeedback: (isHelpful: boolean) => void;
}

export const DocsContent = ({
  selectedSection,
  contentRefs,
  helpful,
  handleFeedback,
}: DocsContentProps) => {
  const renderContent = () => {
    switch (selectedSection) {
      case "overview":
      case "datasetSize":
        return (
          <div ref={contentRefs.overview}>
            <h2 className="text-3xl font-extrabold mb-6 text-gray-800">
              Dataset Overview
            </h2>
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              The dataset is specifically built to test the ability of language
              models (LLMs) to identify hidden rules through reasoning. It
              includes:
            </p>
            <ul className="list-disc list-inside text-gray-700 text-lg mb-6">
              <li>
                <strong>Static Dataset:</strong> Contains fixed rules and
                examples, offering consistent and controlled testing
                environments.
              </li>
              <li>
                <strong>Dynamic Dataset:</strong> Creates new rules and examples
                in real-time to keep challenges fresh and prevent memorization.
              </li>
            </ul>
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              The dataset is used in four types of games:{" "}
              <strong>Static Picnic</strong>, <strong>Dynamic Picnic</strong>,
              <strong>Code Functions Picnic</strong>, and{" "}
              <strong>Math Game</strong>. These games focus on different
              reasoning challenges like pattern recognition, logical deduction,
              and solving math problems.
            </p>

            <div
              ref={contentRefs.datasetSize}
              className="mt-8 bg-gray-50 p-6 rounded-lg shadow-sm"
            >
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Dataset Size
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                The dataset contains over{" "}
                <strong>1,000 unique game scenarios</strong>:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg my-4">
                <li>
                  <strong>Static Dataset:</strong> Includes 250 pre-made rules
                  using 511 items from the Google Open Images Dataset, organized
                  into categories like "personal care" or "furniture."
                </li>
                <li>
                  <strong>Dynamic Dataset:</strong> Generates new rules and
                  examples in real-time, ensuring unlimited scenarios for
                  testing adaptability and critical thinking.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed">
                These datasets allow models to be tested on their ability to
                adapt and solve tasks with varying levels of complexity.
              </p>
            </div>
          </div>
        );
      case "gettingStarted":
      case "chooseGame":
      case "playOrPick":
      case "analyzeResults":
        return (
          <div ref={contentRefs.gettingStarted}>
            <h2 className="text-3xl font-extrabold mb-6 text-gray-800">
              Getting Started
            </h2>
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              To begin using the platform, follow these steps to explore the
              games and evaluate language models effectively. Whether you're a
              researcher or just curious about how LLMs work, this guide will
              help you navigate the process.
            </p>

            <div
              ref={contentRefs.chooseGame}
              className="mt-8 bg-gray-50 p-6 rounded-lg shadow-sm"
            >
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Choose a Game
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                Select one of the four available games:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg my-4">
                <li>
                  <strong>Static Picnic:</strong> Test reasoning with fixed
                  rules.
                </li>
                <li>
                  <strong>Dynamic Picnic:</strong> Challenge yourself with
                  real-time rule generation.
                </li>
                <li>
                  <strong>Code Functions Picnic:</strong> Deduce programmatic
                  rules through Python examples.
                </li>
                <li>
                  <strong>Math Game:</strong> Solve mathematical patterns and
                  relationships.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed">
                Each game is designed to evaluate different aspects of
                reasoning, so pick the one that aligns with your goals.
              </p>
            </div>

            <div
              ref={contentRefs.playOrPick}
              className="mt-8 bg-white p-6 rounded-lg shadow-sm"
            >
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Play or Pick LLMs
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                You can choose between two modes:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg my-4">
                <li>
                  <strong>Play Yourself:</strong> Engage directly with the games
                  to experience the challenges firsthand.
                </li>
                <li>
                  <strong>Observe LLMs:</strong> Select and watch language
                  models like GPT-4 or Claude play the games, analyzing their
                  strategies and decisions.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed">
                This flexibility allows you to either test your own reasoning
                skills or evaluate LLM performance across scenarios.
              </p>
            </div>

            <div
              ref={contentRefs.analyzeResults}
              className="mt-8 bg-gray-50 p-6 rounded-lg shadow-sm"
            >
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Analyze Results
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                After playing or observing the games, review the detailed
                performance metrics:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg my-4">
                <li>
                  <strong>Turns Taken:</strong> Number of attempts used to
                  deduce the rule.
                </li>
                <li>
                  <strong>Examples Seen:</strong> Quantity of examples used
                  during gameplay.
                </li>
                <li>
                  <strong>Time Taken:</strong> Total time spent to complete the
                  task.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed">
                Use these metrics to compare strategies, evaluate LLM reasoning
                abilities, or identify areas for improvement.
              </p>
            </div>
          </div>
        );
      case "paradigm":
        return (
          <div ref={contentRefs.paradigm}>
            <h2 className="text-3xl font-extrabold mb-6 text-gray-800">
              Paradigm
            </h2>
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              The GuessTheRuleBench follows a structured, turn-based interaction
              paradigm. In this setup, a Game Master presents examples based on
              a hidden rule, and the Player (either a human or an LLM) attempts
              to deduce the rule by analyzing the examples.
            </p>
            <div className="mt-6 bg-gray-50 p-6 rounded-lg shadow-sm">
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                How It Works
              </h3>
              <ol className="list-decimal list-inside text-gray-700 text-lg space-y-3">
                <li>
                  The Game Master starts the game by providing an initial set of
                  examples (positive and negative).
                </li>
                <li>
                  The Player can either make a guess about the hidden rule or
                  request more examples.
                </li>
                <li>
                  The game ends when the Player correctly guesses the rule, the
                  maximum number of turns is reached, or the Game Master runs
                  out of examples.
                </li>
              </ol>
            </div>
            <p className="text-gray-700 text-lg leading-relaxed mt-6">
              This paradigm is designed to evaluate reasoning abilities
              systematically by encouraging players to form and test hypotheses
              iteratively. It supports dynamic adaptability, ensuring that both
              static and real-time rule challenges are engaging and robust.
            </p>
          </div>
        );

      case "staticDataset":
      case "picnicGame":
        return (
          <div ref={contentRefs.staticDataset}>
            <h2 className="text-3xl font-extrabold mb-6 text-gray-800">
              Static Dataset
            </h2>
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              The static dataset consists of pre-defined rules and examples that
              remain fixed for each game instance. This ensures consistency in
              evaluation, allowing models to be tested under controlled
              conditions. The dataset is drawn from the Google Open Images
              Dataset and includes a wide variety of categories such as
              "personal care items" or "furniture," enabling comprehensive
              reasoning tasks.
            </p>
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              Static datasets are particularly useful for assessing how well
              models can detect and apply patterns without relying on real-time
              generation. This approach ensures the repeatability of experiments
              and supports benchmarking across different models.
            </p>

            <div
              ref={contentRefs.picnicGame}
              className="mt-8 bg-gray-50 p-6 rounded-lg shadow-sm"
            >
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Picnic Game
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed mb-4">
                The Picnic Game is a reasoning challenge where players deduce
                the hidden rule that determines which items can or cannot be
                "brought to a picnic." The rules are based on specific
                categories, such as:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg space-y-3">
                <li>
                  <strong>L1:</strong> Items from a single category, such as
                  "personal care items."
                </li>
                <li>
                  <strong>L2:</strong> Items from a combination of two
                  categories.
                </li>
                <li>
                  <strong>L3:</strong> Items from three or more categories,
                  introducing higher complexity.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed mt-4">
                The Picnic Game evaluates how well players (humans or LLMs) can
                generalize patterns and apply logical reasoning based on static
                data. It uses 250 pre-defined rules and 511 unique real-world
                items, making it a scalable and interpretable benchmark for
                reasoning tasks.
              </p>
            </div>
          </div>
        );

      case "dynamicDataset":
      case "syntaxGame":
      case "mathSequence":
      case "codeFunctions":
        return (
          <div ref={contentRefs.dynamicDataset}>
            <h2 className="text-3xl font-extrabold mb-6 text-gray-800">
              Dynamic Dataset
            </h2>
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              The dynamic dataset generates rules and examples in real-time,
              offering an adaptive and ever-changing challenge for players.
              Unlike static datasets, these rules are created on the fly by
              leveraging LLMs, ensuring that each game instance is unique. This
              approach prevents memorization and provides a robust test of
              reasoning and adaptability.
            </p>
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              Dynamic datasets categorize rules into five types:
              attribute-based, categorical, logical, relational, and semantic.
              Rules and examples are validated to ensure consistency and
              solvability, making these games ideal for testing a model’s
              ability to infer, adapt, and solve complex problems.
            </p>

            <div
              ref={contentRefs.syntaxGame}
              className="mt-8 bg-gray-50 p-6 rounded-lg shadow-sm"
            >
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Syntax Game
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                The Syntax Game challenges players to deduce hidden rules based
                on grammatical structures and language syntax. Examples provided
                by the Game Master are crafted to reflect specific patterns,
                such as:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg space-y-3">
                <li>
                  Words following specific grammatical categories (e.g., nouns,
                  verbs).
                </li>
                <li>
                  Rules based on sentence structures or semantic relationships.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed mt-4">
                This game tests the model's understanding of language, its
                ability to recognize patterns, and its skill in semantic and
                syntactic reasoning.
              </p>
            </div>

            <div
              ref={contentRefs.mathSequence}
              className="mt-8 bg-white p-6 rounded-lg shadow-sm"
            >
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Mathematical Sequence
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                The Mathematical Sequence game focuses on identifying numerical
                patterns and relationships. The Game Master provides sequences
                that follow specific mathematical rules, such as:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg space-y-3">
                <li>Arithmetic or geometric progressions.</li>
                <li>
                  Rules that vary based on the index (e.g., odd-indexed terms
                  use one rule, even-indexed terms use another).
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed mt-4">
                The game evaluates the player’s ability to analyze numerical
                relationships, apply mathematical operations, and adapt to
                multi-layered rules.
              </p>
            </div>

            <div
              ref={contentRefs.codeFunctions}
              className="mt-8 bg-gray-50 p-6 rounded-lg shadow-sm"
            >
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Code Functions Picnic Game
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                The Code Functions Picnic Game tests the ability to deduce
                programmatic rules using Python string manipulation. The Game
                Master generates rules dynamically and validates the examples
                using an agentic code execution loop. Challenges in this game
                include:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg space-y-3">
                <li>Understanding and deducing programmatic logic.</li>
                <li>Handling ambiguous rules or poorly distributed outputs.</li>
                <li>Ensuring rules are consistent and solvable.</li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed mt-4">
                This game specifically targets LLMs' reasoning capabilities with
                code snippets. However, current models often struggle with this
                task due to poor self-correction and limited ability to infer
                meta-level patterns.
              </p>
            </div>
          </div>
        );

      case "results":
        return (
          <div ref={contentRefs.results}>
            <h2 className="text-3xl font-extrabold mb-6 text-gray-800">
              Experiment Results
            </h2>
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              The experiments were conducted using four leading language models:
              GPT-4o, GPT-4o Mini, Claude 3.5 Haiku, and Claude 3 Haiku. Each
              model was tested across all four games—Static Picnic, Dynamic
              Picnic, Code Functions Picnic, and Math Game—at three difficulty
              levels (L1, L2, L3). Here are the key findings:
            </p>

            <div className="mt-8 bg-gray-50 p-6 rounded-lg shadow-sm">
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Static Picnic Results
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                Models performed best in the Static Picnic game, achieving an
                average win rate of <strong>78.3%</strong> across all difficulty
                levels:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg space-y-3">
                <li>
                  <strong>GPT-4o:</strong> Highest performance at L2 and L3
                  difficulty levels.
                </li>
                <li>
                  <strong>Claude 3 Haiku:</strong> Stronger performance at L1
                  difficulty level.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed">
                These results highlight that models perform well under static
                conditions with pre-defined rules.
              </p>
            </div>

            <div className="mt-8 bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Dynamic Picnic Results
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                The Dynamic Picnic game presented a greater challenge, with an
                average win rate of <strong>39.5%</strong>:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg space-y-3">
                <li>
                  <strong>Claude 3 Haiku:</strong> Achieved the highest win
                  rates at all difficulty levels (L1: 90%, L2: 80%, L3: 73.3%).
                </li>
                <li>
                  <strong>Other models:</strong> Struggled significantly, with
                  none surpassing a 50% win rate.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed">
                These results indicate that dynamic rule generation remains a
                substantial challenge for LLMs.
              </p>
            </div>

            <div className="mt-8 bg-gray-50 p-6 rounded-lg shadow-sm">
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Code Functions Picnic Results
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                None of the models were able to successfully solve the Code
                Functions Picnic game. The following issues were observed:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg space-y-3">
                <li>
                  Models struggled with string manipulation and programmatic
                  reasoning.
                </li>
                <li>
                  Common failures included hallucinating incorrect rules and
                  making incoherent claims.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed">
                These findings highlight a significant limitation of current
                LLMs in handling programmatic and meta-level reasoning tasks.
              </p>
            </div>

            <div className="mt-8 bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">
                Math Game Results
              </h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                Performance in the Math Game varied by difficulty level:
              </p>
              <ul className="list-disc list-inside text-gray-700 text-lg space-y-3">
                <li>
                  All models achieved a <strong>100% win rate</strong> at L1
                  (basic operations).
                </li>
                <li>
                  Performance declined significantly at higher difficulty levels
                  (L2 and L3), requiring index-based rules.
                </li>
                <li>
                  <strong>GPT-4o:</strong> Best performance at L3 with a 60% win
                  rate.
                </li>
              </ul>
              <p className="text-gray-700 text-lg leading-relaxed">
                These results demonstrate that while LLMs excel at simpler
                mathematical patterns, they struggle with complex and
                multi-layered rules.
              </p>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center text-gray-500 mt-8">
            Select a section from the sidebar to view its content
          </div>
        );
    }
  };

  return (
    <ScrollArea className="flex-1 h-screen">
      <div className="max-w-4xl mx-auto py-8 px-6 space-y-8">
        {renderContent()}

        {selectedSection && (
          <>
            <Separator className="my-8" />
            <div className="flex items-center justify-center space-x-8">
              <p className="text-gray-600">Was this helpful?</p>
              <button
                onClick={() => handleFeedback(true)}
                className={cn(
                  "p-2 rounded-full transition-colors duration-200",
                  helpful === true ? "bg-green-100" : "hover:bg-gray-100"
                )}
              >
                <ThumbsUp
                  className={cn(
                    "w-6 h-6",
                    helpful === true ? "text-green-600" : "text-gray-400"
                  )}
                />
              </button>
              <button
                onClick={() => handleFeedback(false)}
                className={cn(
                  "p-2 rounded-full transition-colors duration-200",
                  helpful === false ? "bg-red-100" : "hover:bg-gray-100"
                )}
              >
                <ThumbsDown
                  className={cn(
                    "w-6 h-6",
                    helpful === false ? "text-red-600" : "text-gray-400"
                  )}
                />
              </button>
            </div>
          </>
        )}
      </div>
    </ScrollArea>
  );
};
