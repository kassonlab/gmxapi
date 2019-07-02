#include <memory>

int main()
{
    std::unique_ptr<int> ptr = std::make_unique<int>(0);
    return *ptr;
}
