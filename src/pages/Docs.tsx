import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { useEffect, useRef } from "react";

const Docs = () => {
  const contentRefs = {
    overview: useRef<HTMLDivElement>(null),
    datasetSize: useRef<HTMLDivElement>(null),
    paradigm: useRef<HTMLDivElement>(null),
    staticDataset: useRef<HTMLDivElement>(null),
    picnicGame: useRef<HTMLDivElement>(null),
    dynamicDataset: useRef<HTMLDivElement>(null),
    syntaxGame: useRef<HTMLDivElement>(null),
    mathSequence: useRef<HTMLDivElement>(null),
    results: useRef<HTMLDivElement>(null),
  };

  const scrollToSection = (sectionRef: React.RefObject<HTMLDivElement>) => {
    sectionRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const SidebarItem = ({ 
    title, 
    onClick, 
    indent = false 
  }: { 
    title: string; 
    onClick: () => void; 
    indent?: boolean;
  }) => (
    <div
      className={cn(
        "cursor-pointer hover:text-primary transition-colors duration-200",
        indent ? "ml-4" : ""
      )}
      onClick={onClick}
    >
      {title}
    </div>
  );

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white/80 backdrop-blur-sm border-r shadow-sm">
        <ScrollArea className="h-screen py-6 px-4">
          <div className="space-y-4">
            <div className="font-semibold text-lg mb-2">Documentation</div>
            <SidebarItem 
              title="Dataset Overview" 
              onClick={() => scrollToSection(contentRefs.overview)} 
            />
            <SidebarItem 
              title="Dataset Size" 
              onClick={() => scrollToSection(contentRefs.datasetSize)}
              indent 
            />
            <SidebarItem 
              title="Paradigm" 
              onClick={() => scrollToSection(contentRefs.paradigm)} 
            />
            <SidebarItem 
              title="Static Dataset" 
              onClick={() => scrollToSection(contentRefs.staticDataset)} 
            />
            <SidebarItem 
              title="Picnic Game" 
              onClick={() => scrollToSection(contentRefs.picnicGame)}
              indent 
            />
            <SidebarItem 
              title="Dynamic Dataset" 
              onClick={() => scrollToSection(contentRefs.dynamicDataset)} 
            />
            <SidebarItem 
              title="Syntax Game" 
              onClick={() => scrollToSection(contentRefs.syntaxGame)}
              indent 
            />
            <SidebarItem 
              title="Mathematical Sequence" 
              onClick={() => scrollToSection(contentRefs.mathSequence)}
              indent 
            />
            <SidebarItem 
              title="Experiment Results" 
              onClick={() => scrollToSection(contentRefs.results)} 
            />
          </div>
        </ScrollArea>
      </div>

      {/* Main Content */}
      <ScrollArea className="flex-1 h-screen">
        <div className="max-w-4xl mx-auto py-8 px-6 space-y-8">
          <div ref={contentRefs.overview}>
            <h2 className="text-2xl font-bold mb-4">Dataset Overview</h2>
            <p className="text-gray-700 leading-relaxed">
              The Guess The Rule dataset is designed to test and evaluate the reasoning capabilities
              of language models through interactive gameplay. It consists of both static and dynamic
              rule-based scenarios that challenge players to discover underlying patterns and rules.
            </p>
          </div>

          <Separator className="my-8" />

          <div ref={contentRefs.datasetSize}>
            <h3 className="text-xl font-semibold mb-4">Dataset Size</h3>
            <p className="text-gray-700 leading-relaxed">
              Our dataset comprises over 1,000 unique game scenarios, split between static and
              dynamic rule sets. Each scenario is carefully crafted to test different aspects of
              logical reasoning and pattern recognition.
            </p>
          </div>

          <Separator className="my-8" />

          <div ref={contentRefs.paradigm}>
            <h2 className="text-2xl font-bold mb-4">Paradigm</h2>
            <p className="text-gray-700 leading-relaxed">
              The game follows a turn-based interaction paradigm where players propose examples
              and receive feedback. This structure allows for systematic evaluation of reasoning
              capabilities and hypothesis testing strategies.
            </p>
          </div>

          <Separator className="my-8" />

          <div ref={contentRefs.staticDataset}>
            <h2 className="text-2xl font-bold mb-4">Static Dataset</h2>
            <p className="text-gray-700 leading-relaxed">
              Static datasets feature predetermined rules and patterns that remain consistent
              across all gameplay sessions. These scenarios provide a controlled environment
              for evaluating basic reasoning capabilities.
            </p>
          </div>

          <Separator className="my-8" />

          <div ref={contentRefs.picnicGame}>
            <h3 className="text-xl font-semibold mb-4">Picnic Game</h3>
            <p className="text-gray-700 leading-relaxed">
              The Picnic Game is a classic example of our static dataset challenges. Players
              must deduce the hidden rule that determines which items are allowed at a picnic,
              based on specific linguistic or logical patterns.
            </p>
          </div>

          <Separator className="my-8" />

          <div ref={contentRefs.dynamicDataset}>
            <h2 className="text-2xl font-bold mb-4">Dynamic Dataset</h2>
            <p className="text-gray-700 leading-relaxed">
              Dynamic datasets introduce variable rules and patterns that can adapt or change
              during gameplay. These scenarios test advanced reasoning and adaptation capabilities.
            </p>
          </div>

          <Separator className="my-8" />

          <div ref={contentRefs.syntaxGame}>
            <h3 className="text-xl font-semibold mb-4">Syntax Game</h3>
            <p className="text-gray-700 leading-relaxed">
              The Syntax Game challenges players to discover rules based on grammatical structures
              and linguistic patterns. This tests understanding of language syntax and semantic
              relationships.
            </p>
          </div>

          <Separator className="my-8" />

          <div ref={contentRefs.mathSequence}>
            <h3 className="text-xl font-semibold mb-4">Mathematical Sequence</h3>
            <p className="text-gray-700 leading-relaxed">
              Mathematical sequence challenges focus on numerical patterns and relationships.
              Players must identify underlying mathematical rules through systematic testing
              and observation.
            </p>
          </div>

          <Separator className="my-8" />

          <div ref={contentRefs.results}>
            <h2 className="text-2xl font-bold mb-4">Experiment Results</h2>
            <p className="text-gray-700 leading-relaxed">
              Our experiments have shown varying success rates across different language models
              and rule types. Static rules generally see higher success rates, while dynamic
              rules present more significant challenges, particularly in cases requiring
              adaptive reasoning.
            </p>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
};

export default Docs;