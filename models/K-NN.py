import numpy as np

def compute_optimal_weights(k, d):
    """
    Compute the asymptotically optimal weights for the k-NN classifier.
    
    For i = 1, ..., k the weight is given by
      w_i = (1/k) * (1 + d/2 - d/(2*k^(2/d))) / [ i^(1+2/d) - (i-1)^(1+2/d) ]
    and then normalized so that the weights sum to 1.
    
    Args:
        k (int): Number of neighbors.
        d (int): Dimension of the feature space.
    
    Returns:
        numpy.ndarray: An array of length k containing the normalized weights.
    """
    weights = np.zeros(k)
    constant = 1.0 / k * (1 + d/2 - d/(2 * (k ** (2/d))))
    for i in range(1, k+1):
        denominator = (i ** (1 + 2/d)) - ((i - 1) ** (1 + 2/d))
        weights[i-1] = constant / denominator
    # Normalize weights so that they sum to 1.
    weights /= np.sum(weights)
    return weights

def loocv_error(X, Y, k, d):
    """
    Compute the leave-one-out cross-validation (LOOCV) error for the weighted k-NN classifier.
    
    For each observation j, we leave it out, compute distances from X[j] to the other points,
    sort them, take the first k neighbors, and then classify using the weighted vote:
        predict 1 if sum(weights * 1{neighbor==1}) >= 0.5, else predict 2.
    
    Args:
        X (numpy.ndarray): Array of shape (n, d) containing the features.
        Y (numpy.ndarray): Array of shape (n,) containing the class labels (1 or 2).
        k (int): Number of neighbors to use.
        d (int): Feature dimension.
    
    Returns:
        float: The LOOCV error rate.
    """
    n = X.shape[0]
    weights = compute_optimal_weights(k, d)
    errors = 0
    for j in range(n):
        # Leave out the j-th observation.
        X_train = np.delete(X, j, axis=0)
        Y_train = np.delete(Y, j, axis=0)
        test_point = X[j]
        
        # Compute Euclidean distances from the test point to all training points.
        distances = np.linalg.norm(X_train - test_point, axis=1)
        sorted_idx = np.argsort(distances)
        neighbor_labels = Y_train[sorted_idx[:k]]
        
        # Compute weighted vote (using indicator function for class 1).
        vote = np.sum(weights * (neighbor_labels == 1))
        pred = 1 if vote >= 0.5 else 2
        if pred != Y[j]:
            errors += 1
    return errors / n

def select_best_k(X, Y, candidate_ks, d):
    """
    Select the best number of neighbors (k) based on LOOCV error.
    
    Args:
        X (numpy.ndarray): Training features of shape (n, d).
        Y (numpy.ndarray): Training labels of shape (n,).
        candidate_ks (list or iterable): Candidate values for k.
        d (int): Feature dimension.
    
    Returns:
        tuple: (best_k, best_error)
    """
    best_k = None
    best_error = float('inf')
    for k in candidate_ks:
        error = loocv_error(X, Y, k, d)
        print(f"Candidate k = {k}, LOOCV error = {error:.4f}")
        if error < best_error:
            best_error = error
            best_k = k
    return best_k, best_error

class WeightedKNNClassifier:
    """
    A weighted k-NN classifier that uses asymptotically optimal weights.
    """
    def __init__(self, k, d):
        """
        Initialize the classifier.
        
        Args:
            k (int): Number of neighbors to use.
            d (int): Feature dimension.
        """
        self.k = k
        self.d = d
        self.weights = compute_optimal_weights(k, d)
        self.X_train = None
        self.Y_train = None

    def fit(self, X, Y):
        """
        Fit the classifier by storing the training data.
        
        Args:
            X (numpy.ndarray): Training features of shape (n, d).
            Y (numpy.ndarray): Training labels of shape (n,).
        """
        self.X_train = X
        self.Y_train = Y

    def predict(self, X_test):
        """
        Predict the labels for test data.
        
        Args:
            X_test (numpy.ndarray): Test features of shape (m, d).
        
        Returns:
            numpy.ndarray: Predicted class labels (1 or 2) for each test instance.
        """
        m = X_test.shape[0]
        predictions = np.zeros(m, dtype=int)
        for j in range(m):
            test_point = X_test[j]
            distances = np.linalg.norm(self.X_train - test_point, axis=1)
            sorted_idx = np.argsort(distances)
            neighbor_labels = self.Y_train[sorted_idx[:self.k]]
            vote = np.sum(self.weights * (neighbor_labels == 1))
            predictions[j] = 1 if vote >= 0.5 else 2
        return predictions

def main():
    """
    Main training routine:
      1. (Optionally) Load or generate your dataset D = {(X_i, Y_i)}.
      2. Use LOOCV to select the best k (and corresponding weights).
      3. Train the final weighted k-NN classifier on the full dataset.
    """
    # === Example: Create a synthetic dataset ===
    # In practice, replace this with code to load your own dataset.
    np.random.seed(0)
    n = 100      # sample size
    d = 2        # feature dimension
    # Generate synthetic data for two classes.
    X_class1 = np.random.randn(n//2, d) + np.array([1, 1])
    X_class2 = np.random.randn(n//2, d) + np.array([-1, -1])
    X = np.vstack((X_class1, X_class2))
    Y = np.array([1]*(n//2) + [2]*(n//2))

    # === Hyperparameter selection via LOOCV ===
    candidate_ks = list(range(1, 21))  # try k = 1, 2, ..., 20
    best_k, best_error = select_best_k(X, Y, candidate_ks, d)
    print(f"\nSelected best k = {best_k} with LOOCV error = {best_error:.4f}\n")

    # === Train final classifier ===
    clf = WeightedKNNClassifier(k=best_k, d=d)
    clf.fit(X, Y)
    
    # (Optional) Evaluate performance on training data.
    predictions = clf.predict(X)
    accuracy = np.mean(predictions == Y)
    print(f"Training accuracy: {accuracy:.4f}")

if __name__ == "__main__":
    main()
