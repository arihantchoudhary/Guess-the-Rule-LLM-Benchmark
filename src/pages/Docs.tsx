import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState, useRef } from "react";

const Docs = () => {
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [helpful, setHelpful] = useState<boolean | null>(null);

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

  const toggleSection = (section: string) => {
    setOpenSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const scrollToSection = (sectionRef: React.RefObject<HTMLDivElement>, section: string) => {
    setSelectedSection(section);
    sectionRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleFeedback = (isHelpful: boolean) => {
    setHelpful(isHelpful);
    // Here you could add API call to save feedback
    console.log(`User found the documentation ${isHelpful ? 'helpful' : 'not helpful'}`);
  };

  return (
    <div className="flex min-h-screen bg-white">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r shadow-sm">
        <ScrollArea className="h-screen py-6 px-4">
          <div className="space-y-4">
            <Collapsible>
              <CollapsibleTrigger 
                onClick={() => toggleSection('overview')}
                className="font-semibold text-lg mb-2 w-full text-left hover:text-primary transition-colors duration-200"
              >
                Dataset Overview
              </CollapsibleTrigger>
              <CollapsibleContent>
                {openSections['overview'] && (
                  <div 
                    className="ml-4 cursor-pointer hover:text-primary transition-colors duration-200"
                    onClick={() => scrollToSection(contentRefs.datasetSize, 'datasetSize')}
                  >
                    Dataset Size
                  </div>
                )}
              </CollapsibleContent>
            </Collapsible>

            <div 
              className="cursor-pointer hover:text-primary transition-colors duration-200"
              onClick={() => scrollToSection(contentRefs.paradigm, 'paradigm')}
            >
              Paradigm
            </div>

            <Collapsible>
              <CollapsibleTrigger 
                onClick={() => toggleSection('static')}
                className="font-semibold text-lg mb-2 w-full text-left hover:text-primary transition-colors duration-200"
              >
                Static Dataset
              </CollapsibleTrigger>
              <CollapsibleContent>
                {openSections['static'] && (
                  <div 
                    className="ml-4 cursor-pointer hover:text-primary transition-colors duration-200"
                    onClick={() => scrollToSection(contentRefs.picnicGame, 'picnicGame')}
                  >
                    Picnic Game
                  </div>
                )}
              </CollapsibleContent>
            </Collapsible>

            <Collapsible>
              <CollapsibleTrigger 
                onClick={() => toggleSection('dynamic')}
                className="font-semibold text-lg mb-2 w-full text-left hover:text-primary transition-colors duration-200"
              >
                Dynamic Dataset
              </CollapsibleTrigger>
              <CollapsibleContent>
                {openSections['dynamic'] && (
                  <>
                    <div 
                      className="ml-4 cursor-pointer hover:text-primary transition-colors duration-200"
                      onClick={() => scrollToSection(contentRefs.syntaxGame, 'syntaxGame')}
                    >
                      Syntax Game
                    </div>
                    <div 
                      className="ml-4 cursor-pointer hover:text-primary transition-colors duration-200"
                      onClick={() => scrollToSection(contentRefs.mathSequence, 'mathSequence')}
                    >
                      Mathematical Sequence
                    </div>
                  </>
                )}
              </CollapsibleContent>
            </Collapsible>

            <div 
              className="cursor-pointer hover:text-primary transition-colors duration-200"
              onClick={() => scrollToSection(contentRefs.results, 'results')}
            >
              Experiment Results
            </div>
          </div>
        </ScrollArea>
      </div>

      {/* Main Content */}
      <ScrollArea className="flex-1 h-screen">
        <div className="max-w-4xl mx-auto py-8 px-6 space-y-8">
          {selectedSection === 'datasetSize' && (
            <div ref={contentRefs.datasetSize}>
              <h3 className="text-xl font-semibold mb-4">Dataset Size</h3>
              <p className="text-gray-700 leading-relaxed">
                Our dataset comprises over 1,000 unique game scenarios, split between static and
                dynamic rule sets. Each scenario is carefully crafted to test different aspects of
                logical reasoning and pattern recognition.
              </p>
            </div>
          )}

          {selectedSection === 'paradigm' && (
            <div ref={contentRefs.paradigm}>
              <h2 className="text-2xl font-bold mb-4">Paradigm</h2>
              <p className="text-gray-700 leading-relaxed">
                The game follows a turn-based interaction paradigm where players propose examples
                and receive feedback. This structure allows for systematic evaluation of reasoning
                capabilities and hypothesis testing strategies.
              </p>
            </div>
          )}

          {selectedSection === 'picnicGame' && (
            <div ref={contentRefs.picnicGame}>
              <h3 className="text-xl font-semibold mb-4">Picnic Game</h3>
              <p className="text-gray-700 leading-relaxed">
                The Picnic Game is a classic example of our static dataset challenges. Players
                must deduce the hidden rule that determines which items are allowed at a picnic,
                based on specific linguistic or logical patterns.
              </p>
            </div>
          )}

          {selectedSection === 'syntaxGame' && (
            <div ref={contentRefs.syntaxGame}>
              <h3 className="text-xl font-semibold mb-4">Syntax Game</h3>
              <p className="text-gray-700 leading-relaxed">
                The Syntax Game challenges players to discover rules based on grammatical structures
                and linguistic patterns. This tests understanding of language syntax and semantic
                relationships.
              </p>
            </div>
          )}

          {selectedSection === 'mathSequence' && (
            <div ref={contentRefs.mathSequence}>
              <h3 className="text-xl font-semibold mb-4">Mathematical Sequence</h3>
              <p className="text-gray-700 leading-relaxed">
                Mathematical sequence challenges focus on numerical patterns and relationships.
                Players must identify underlying mathematical rules through systematic testing
                and observation.
              </p>
            </div>
          )}

          {selectedSection === 'results' && (
            <div ref={contentRefs.results}>
              <h2 className="text-2xl font-bold mb-4">Experiment Results</h2>
              <p className="text-gray-700 leading-relaxed">
                Our experiments have shown varying success rates across different language models
                and rule types. Static rules generally see higher success rates, while dynamic
                rules present more significant challenges, particularly in cases requiring
                adaptive reasoning.
              </p>
            </div>
          )}

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
                  <ThumbsUp className={cn(
                    "w-6 h-6",
                    helpful === true ? "text-green-600" : "text-gray-400"
                  )} />
                </button>
                <button
                  onClick={() => handleFeedback(false)}
                  className={cn(
                    "p-2 rounded-full transition-colors duration-200",
                    helpful === false ? "bg-red-100" : "hover:bg-gray-100"
                  )}
                >
                  <ThumbsDown className={cn(
                    "w-6 h-6",
                    helpful === false ? "text-red-600" : "text-gray-400"
                  )} />
                </button>
              </div>
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

export default Docs;