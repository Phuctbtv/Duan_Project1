

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,   
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    phone_number VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('customer', 'employee', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    id_card_number VARCHAR(20) UNIQUE,
    nationality VARCHAR(50),
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)   
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS InsuranceProducts (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    coverage_details TEXT,
    terms_and_conditions TEXT,
    premium_base_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(5) DEFAULT 'VND',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Policies (
    policy_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    premium_amount DECIMAL(10, 2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('pending', 'paid', 'overdue', 'cancelled')),
    policy_status VARCHAR(20) NOT NULL CHECK (policy_status IN ('active', 'expired', 'cancelled', 'pending')),
    policy_document_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES Customers(customer_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_product
        FOREIGN KEY (product_id)
        REFERENCES InsuranceProducts(product_id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS PolicyHolders (
    holder_id SERIAL PRIMARY KEY,
    policy_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    id_card_number VARCHAR(20),
    relationship_to_customer VARCHAR(50),
    CONSTRAINT fk_policy_holder
        FOREIGN KEY (policy_id)
        REFERENCES Policies(policy_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Payments (
    payment_id SERIAL PRIMARY KEY,
    policy_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('credit_card', 'bank_transfer', 'e_wallet', 'other')),
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'pending')),
    CONSTRAINT fk_policy_payment
        FOREIGN KEY (policy_id)
        REFERENCES Policies(policy_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Claims (
    claim_id SERIAL PRIMARY KEY,
    policy_id INT NOT NULL,
    customer_id INT NOT NULL,
    claim_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    incident_date DATE NOT NULL,
    description TEXT,
    requested_amount DECIMAL(10, 2),
    claim_status VARCHAR(20) NOT NULL CHECK (claim_status IN ('pending', 'in_progress', 'approved', 'rejected', 'settled')),
    approved_amount DECIMAL(10, 2),
    rejection_reason TEXT,
    settlement_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_policy_claim
        FOREIGN KEY (policy_id)
        REFERENCES Policies(policy_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_customer_claim
        FOREIGN KEY (customer_id)
        REFERENCES Customers(customer_id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ClaimDocuments (
    document_id SERIAL PRIMARY KEY,
    claim_id INT NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    file_url VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ocr_extracted_text TEXT,
    ai_analysis_result JSONB,
    CONSTRAINT fk_claim_document
        FOREIGN KEY (claim_id)
        REFERENCES Claims(claim_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('policy_update', 'claim_status', 'payment_reminder', 'promotion', 'other')),
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_notification
        FOREIGN KEY (user_id)
        REFERENCES users(id) -- Corrected foreign key
        ON DELETE CASCADE
);
