"""
Massive centralized dictionary of technical and soft skills across domains.
This ensures almost no skill goes unnoticed during JD and resume processing.
"""

TECHNICAL_SKILLS = {
    # -----------------------------------------------------
    # 1. Programming Languages & Paradigms
    # -----------------------------------------------------
    'python', 'java', 'javascript', 'typescript', 'c', 'c++', 'cpp', 'c#', 'csharp', 
    'ruby', 'go', 'golang', 'rust', 'swift', 'kotlin', 'php', 'r', 'scala', 'perl', 
    'matlab', 'sql', 'html', 'css', 'julia', 'haskell', 'lua', 'bash', 'shell', 
    'powershell', 'assembly', 'dart', 'solidity', 'groovy', 'clojure', 'elixir', 
    'f#', 'fortran', 'cobol', 'lisp', 'prolog', 'vhdl', 'verilog', 'sas', 'vba',
    'object oriented programming', 'oop', 'functional programming', 'scripting',

    # -----------------------------------------------------
    # 2. Frontend & Mobile Frameworks
    # -----------------------------------------------------
    'react', 'reactjs', 'react native', 'angular', 'angularjs', 'vue', 'vuejs', 
    'svelte', 'nextjs', 'next.js', 'nuxtjs', 'nuxt.js', 'gatsby', 'emberjs', 'backbone',
    'bootstrap', 'tailwind', 'tailwindcss', 'material ui', 'mui', 'chakra ui', 
    'styled components', 'jquery', 'sass', 'less', 'webpack', 'babel', 'vite',
    'flutter', 'ios', 'android', 'xamarin', 'ionic', 'cordova', 'electron',

    # -----------------------------------------------------
    # 3. Backend Frameworks & Architectures
    # -----------------------------------------------------
    'django', 'flask', 'fastapi', 'spring', 'springboot', 'spring boot', 
    'express', 'expressjs', 'node', 'nodejs', 'rails', 'ruby on rails', 
    'laravel', 'symfony', 'asp.net', 'dot net', '.net', 'flask-restful',
    'microservices', 'monolith', 'serverless', 'event-driven architecture',
    'rest', 'restful', 'graphql', 'grpc', 'soap', 'websocket', 'socket.io', 
    'webhook', 'api', 'apis', 'mvc', 'mvvm',

    # -----------------------------------------------------
    # 4. Databases & Data Stores (SQL, NoSQL, Vector)
    # -----------------------------------------------------
    'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'sqlite', 'oracle', 
    'cassandra', 'dynamodb', 'elasticsearch', 'neo4j', 'firebase', 'supabase', 
    'nosql', 'graphdb', 'sql server', 'mariadb', 'cockroachdb', 'couchdb', 
    'arango', 'memcached', 'cosmos db', 'riak',
    # Vector DBs
    'pinecone', 'weaviate', 'chromadb', 'milvus', 'faiss', 'qdrant', 'zilliz',

    # -----------------------------------------------------
    # 5. Cloud, DevOps, CI/CD, & Infrastructure
    # -----------------------------------------------------
    'aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'digitalocean', 
    'heroku', 'vercel', 'netlify', 'cloud computing',
    'docker', 'kubernetes', 'k8s', 'docker compose', 'helm', 
    'jenkins', 'terraform', 'ansible', 'chef', 'puppet', 'ci/cd', 'cicd', 
    'github actions', 'circleci', 'travis ci', 'gitlab ci', 'bitbucket pipelines',
    'linux', 'unix', 'ubuntu', 'centos', 'debian', 'redhat',
    'git', 'github', 'gitlab', 'bitbucket', 'svn', 'version control',
    'nginx', 'apache', 'iis', 'tomcat', 'caddy',
    'lambda', 'ec2', 's3', 'ecs', 'eks', 'sagemaker', 'vertex ai', 'cloudformation',
    'prometheus', 'grafana', 'datadog', 'new relic', 'splunk', 'elk stack',
    'istio', 'service mesh', 'vault', 'consul',

    # -----------------------------------------------------
    # 6. Data Engineering & Big Data
    # -----------------------------------------------------
    'data engineering', 'data pipelines', 'etl', 'elt', 'big data',
    'hadoop', 'spark', 'pyspark', 'kafka', 'airflow', 'luigi', 'nifi',
    'dbt', 'snowflake', 'databricks', 'redshift', 'bigquery', 'athena',
    'flink', 'beam', 'kinesis', 'sqs', 'sns', 'rabbitmq', 'activemq',
    'tableau', 'power bi', 'looker', 'metabase', 'qlik', 'superset',
    'data warehousing', 'data lakes', 'data modeling',

    # -----------------------------------------------------
    # 7. AI, Machine Learning & MLOps
    # -----------------------------------------------------
    'machine learning', 'deep learning', 'nlp', 'natural language processing', 
    'computer vision', 'reinforcement learning', 'supervised learning', 
    'unsupervised learning', 'transfer learning', 'neural networks', 
    'cnn', 'rnn', 'lstm', 'gru', 'transformer', 'transformers', 'bert',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 
    'jax', 'flax', 'xgboost', 'lightgbm', 'catboost', 'theano', 'caffe',
    'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'bokeh',
    'opencv', 'pillow', 'scikit-image', 'spacy', 'nltk', 'gensim', 'textblob',
    'hugging face', 'huggingface', 
    'data science', 'data analysis', 'feature engineering', 'hyperparameter tuning', 
    'cross validation', 'time series', 'forecasting', 'anomaly detection', 
    'recommendation systems', 'ab testing', 'a/b testing',
    'mlops', 'mlflow', 'kubeflow', 'wandb', 'weights and biases', 
    'experiment tracking', 'model evaluation', 'model deployment',

    # -----------------------------------------------------
    # 8. Generative AI & Large Language Models (LLMs)
    # -----------------------------------------------------
    'llm', 'llms', 'large language models', 'gpt', 'gpt-3', 'gpt-4', 'chatgpt', 
    'openai', 'claude', 'anthropic', 'gemini', 'llama', 'llama 2', 'llama 3', 
    'mistral', 'palm', 'cohere', 'falcon',
    'langchain', 'llamaindex', 'autogen', 'crewai', 'semantic kernel',
    'rag', 'retrieval augmented generation', 'retrieval-augmented generation',
    'prompt engineering', 'fine-tuning', 'fine tuning', 'instruction tuning',
    'rlhf', 'sft', 'dpo', 'ppo', 'reward modeling',
    'diffusion models', 'stable diffusion', 'midjourney', 'dall-e',
    'generative ai', 'genai', 'agentic', 'agentic ai', 'ai agents',
    'embeddings', 'vectorization', 'semantic search',
    'lora', 'qlora', 'peft', 'quantization', 'gguf', 'llama.cpp', 'vllm',

    # -----------------------------------------------------
    # 9. Cybersecurity & Networking
    # -----------------------------------------------------
    'cybersecurity', 'security', 'infosec', 'penetration testing', 'pentesting',
    'cryptography', 'encryption', 'ssl', 'tls', 'pki', 'iam', 'oauth2', 'saml', 'oidc',
    'jwt', 'owasp', 'vulnerability assessment', 'incident response', 'firewalls',
    'tcp/ip', 'dns', 'http', 'https', 'ftp', 'ssh', 'vpn', 'load balancing',
    'wireshark', 'nmap', 'kali linux', 'metasploit', 'burp suite',

    # -----------------------------------------------------
    # 10. Software Engineering Practices & Tools
    # -----------------------------------------------------
    'system design', 'design patterns', 'solid principles', 'dry', 'kiss',
    'tdd', 'bdd', 'unit testing', 'integration testing', 'e2e testing',
    'pytest', 'jest', 'mocha', 'chai', 'cypress', 'selenium', 'puppeteer', 'playwright',
    'data structures', 'algorithms', 'dsa', 'competitive programming', 'leetcode',
    'agile', 'scrum', 'kanban', 'sprint', 'jira', 'confluence', 'trello', 'asana',
    'linux kernel', 'os development', 'embedded systems', 'iot', 'arduino', 'raspberry pi',

    # -----------------------------------------------------
    # 11. UI/UX, Design, & Product
    # -----------------------------------------------------
    'ui/ux', 'user interface', 'user experience', 'wireframing', 'prototyping',
    'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator', 'invision',
    'product management', 'product strategy', 'customer discovery',

    # -----------------------------------------------------
    # 12. Hardware, Electronics, & Engineering
    # -----------------------------------------------------
    'pcb design', 'autocad', 'solidworks', 'matlab', 'simulink', 'plc', 'scada',
    'robotics', 'ros', 'cad', 'cam', 'vlsi', 'fpga', 'microcontrollers',

    # -----------------------------------------------------
    # 13. Business, Finance, & Marketing Tech
    # -----------------------------------------------------
    'seo', 'sem', 'digital marketing', 'google analytics', 'salesforce', 'hubspot',
    'crm', 'erp', 'sap', 'blockchain', 'web3', 'smart contracts', 'ethereum',
    'solana', 'bitcoin', 'cryptocurrency', 'fintech', 'quantitative analysis',
}

SOFT_SKILLS = {
    # -----------------------------------------------------
    # Communication & Interpersonal
    # -----------------------------------------------------
    'communication', 'written communication', 'verbal communication', 'public speaking', 
    'presentation', 'storytelling', 'active listening', 'negotiation', 'persuasion',
    'interpersonal', 'empathy', 'emotional intelligence', 'eq', 'networking',
    'stakeholder management', 'client facing', 'customer service', 'collaboration',
    
    # -----------------------------------------------------
    # Teamwork & Leadership
    # -----------------------------------------------------
    'teamwork', 'team player', 'leadership', 'team management', 'mentoring', 
    'coaching', 'conflict resolution', 'cross functional', 'cross-functional',
    'delegation', 'team building', 'motivation',
    
    # -----------------------------------------------------
    # Problem Solving & Critical Thinking
    # -----------------------------------------------------
    'problem solving', 'problem-solving', 'critical thinking', 'analytical',
    'troubleshooting', 'decision making', 'logical reasoning', 'strategic thinking',
    'innovation', 'creativity', 'creative problem solving', 'brainstorming',
    'research', 'data-driven', 'detail oriented', 'detail-oriented', 'attention to detail',
    
    # -----------------------------------------------------
    # Work Ethic & Personal Attributes
    # -----------------------------------------------------
    'work ethic', 'hardworking', 'reliable', 'dependable', 'punctual',
    'ownership', 'initiative', 'proactive', 'self motivated', 'self-starter',
    'self starter', 'fast learner', 'quick learner', 'adaptability', 'flexibility',
    'resilience', 'patience', 'integrity', 'honesty', 'continuous learning',
    'growth mindset', 'curiosity',
    
    # -----------------------------------------------------
    # Management & Organization
    # -----------------------------------------------------
    'time management', 'project management', 'organizational', 'multitasking',
    'prioritization', 'planning', 'scheduling', 'resource management',
    'risk management', 'event management', 'documentation', 'writing',
}
