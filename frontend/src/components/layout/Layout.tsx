import { Link } from "react-router-dom";

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-sm border-b z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-xl font-bold text-primary">
                Guess The Rule Bench
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-sm font-medium hover:text-primary">
                Home
              </Link>
              <Link to="/docs" className="text-sm font-medium hover:text-primary">
                Docs
              </Link>
              <Link to="/play" className="text-sm font-medium hover:text-primary">
                Play Game
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow pt-16">
        {children}
      </main>

      {/* Footer */}
      <footer className="py-8 px-4 border-t bg-white/50">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center">
          <div className="text-sm text-muted-foreground">
            © 2024 Guess The Rule Bench. All rights reserved.
          </div>
          <div className="flex gap-6 mt-4 md:mt-0">
            {/* <a
              href="/privacy"
              className="text-sm text-muted-foreground hover:text-primary"
            >
              Privacy Policy
            </a>
            <a
              href="/contact"
              className="text-sm text-muted-foreground hover:text-primary"
            >
              Contact Us
            </a>
            <a
              href="https://github.com/m1chae11u/Guess-the-Rule-LLM-Benchmark"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-muted-foreground hover:text-primary"
            >
              GitHub
            </a> */}
          </div>
        </div>
      </footer>
    </div>
  );
};