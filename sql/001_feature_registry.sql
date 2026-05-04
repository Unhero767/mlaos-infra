-- Feature Registry Schema (Rule #11: Give feature columns owners)
-- Author: Kenneth Dallmier | kennydallmier@gmail.com

CREATE TABLE IF NOT EXISTS feature_registry (
    feature_id          SERIAL PRIMARY KEY,
    feature_name        VARCHAR(255) NOT NULL UNIQUE,
    owner_email         VARCHAR(255) NOT NULL,
    backup_owner_email  VARCHAR(255),
    description         TEXT NOT NULL,
    data_type           VARCHAR(50) NOT NULL DEFAULT 'FLOAT',
    expected_coverage_pct DECIMAL(5,2) NOT NULL DEFAULT 100.0,
    status              VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
                            CHECK (status IN ('ACTIVE', 'DEPRECATED', 'EXPERIMENTAL')),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at        TIMESTAMP WITH TIME ZONE,
    notes               TEXT
);

CREATE INDEX idx_feature_registry_status ON feature_registry(status);
CREATE INDEX idx_feature_registry_owner ON feature_registry(owner_email);

-- Seed: Core MLAOS features
INSERT INTO feature_registry (
    feature_name, owner_email, backup_owner_email,
    description, data_type, expected_coverage_pct, status
) VALUES
(
    'resonance_score',
    'kennydallmier@gmail.com',
    'kennydallmier@gmail.com',
    'Emotional resonance of memory node (0.0-1.0)',
    'FLOAT', 100.0, 'ACTIVE'
),
(
    'chiaroscuro_index',
    'kennydallmier@gmail.com',
    'kennydallmier@gmail.com',
    'Light/dark contrast ratio for memory polarization (0.0-1.0)',
    'FLOAT', 100.0, 'ACTIVE'
),
(
    'memory_vector',
    'kennydallmier@gmail.com',
    'kennydallmier@gmail.com',
    'Embedding vector representing memory node in latent space',
    'ARRAY', 100.0, 'ACTIVE'
),
(
    'archetype_alignment',
    'kennydallmier@gmail.com',
    'kennydallmier@gmail.com',
    'Cosine similarity to nearest Jungian archetype (0.0-1.0)',
    'FLOAT', 95.0, 'ACTIVE'
)
ON CONFLICT (feature_name) DO NOTHING;
